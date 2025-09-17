"""
MongoDB Interface for Cell Design Storage and Retrieval

This module provides functions to store, fetch, and update cell designs in MongoDB.
It implements a proper database schema with separate collections for users, sessions,
and cell designs with advanced search capabilities.

Database Schema:
- users: Store user information and preferences
- sessions: Store session metadata and user associations
- cell_designs: Store cell design data with searchable fields
"""

import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import DuplicateKeyError, ConnectionFailure

from mcp_server.cell_designer.cell_design import (
    CellDesign,
    PrismaticCellDesignParameters,
    CylindricalCellDesignParameters,
    PouchCellDesignParameters,
)

logger = logging.getLogger(__name__)


class MongoDBCellDesignStorage:
    """MongoDB interface for cell design storage and retrieval with proper schema."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: str = "cell_designs_db",
    ):
        """
        Initialize MongoDB connection.

        Args:
            connection_string: MongoDB connection string. If None, uses environment variable.
            database_name: Name of the database to use.
        """
        self.connection_string = (
            connection_string
            or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db = None

        # Collections
        self.users_collection = None
        self.sessions_collection = None
        self.cell_designs_collection = None

        try:
            self.connect()
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise

    def connect(self):
        """Establish MongoDB connection and set up collections."""
        try:
            self.client = MongoClient(
                self.connection_string, serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command("ping")
            self.db = self.client[self.database_name]

            # Initialize collections
            self.users_collection = self.db.users
            self.sessions_collection = self.db.sessions
            self.cell_designs_collection = self.db.cell_designs

            # Create indexes for users collection
            self.users_collection.create_index([("user_id", ASCENDING)], unique=True)
            self.users_collection.create_index(
                [("email", ASCENDING)], unique=True, sparse=True
            )
            self.users_collection.create_index([("created_at", DESCENDING)])

            # Create indexes for sessions collection
            self.sessions_collection.create_index(
                [("session_id", ASCENDING)], unique=True
            )
            self.sessions_collection.create_index([("user_id", ASCENDING)])
            self.sessions_collection.create_index([("created_at", DESCENDING)])
            self.sessions_collection.create_index([("last_accessed", DESCENDING)])

            # Create indexes for cell_designs collection
            self.cell_designs_collection.create_index(
                [("cell_design_id", ASCENDING)], unique=True
            )
            self.cell_designs_collection.create_index([("session_id", ASCENDING)])
            self.cell_designs_collection.create_index([("user_id", ASCENDING)])
            self.cell_designs_collection.create_index(
                [("cell_design.created_at", DESCENDING)]
            )

            # Indexes for searchable fields within cell_design
            self.cell_designs_collection.create_index(
                [("cell_design.design_hash", ASCENDING)]
            )
            self.cell_designs_collection.create_index(
                [("cell_design.keywords", ASCENDING)]
            )

            # Indexes for cell design parameters
            self.cell_designs_collection.create_index(
                [("cell_design.cell_design_parameters.Form factor", ASCENDING)]
            )

            # Index for bill of materials
            self.cell_designs_collection.create_index(
                [("cell_design.bill_of_materials", ASCENDING)]
            )

            # Compound indexes for common queries
            self.cell_designs_collection.create_index(
                [("cell_design.design_hash", ASCENDING), ("user_id", ASCENDING)]
            )
            self.cell_designs_collection.create_index(
                [("cell_design.keywords", ASCENDING), ("session_id", ASCENDING)]
            )

            # Create text index for full-text search
            self.cell_designs_collection.create_index(
                [
                    ("cell_design.context", TEXT),
                    ("cell_design.description", TEXT),
                    ("cell_design.keywords", TEXT),
                ]
            )

            # Create compound indexes for common queries
            self.cell_designs_collection.create_index(
                [("user_id", ASCENDING), ("cell_design.created_at", DESCENDING)]
            )
            self.cell_designs_collection.create_index(
                [("session_id", ASCENDING), ("cell_design.created_at", DESCENDING)]
            )

            logger.info(
                f"Successfully connected to MongoDB database: {self.database_name}"
            )

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB connection: {e}")
            raise

    def close_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    # ============================================================================
    # User Management Functions
    # ============================================================================

    def create_user(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        preferences: Optional[Dict] = None,
    ) -> str:
        """
        Create a new user.

        Args:
            user_id: Unique user identifier. If None, generates UUID.
            email: User email address
            name: User display name
            preferences: User preferences dictionary

        Returns:
            User ID of created user
        """
        try:
            user_id = user_id or str(uuid.uuid4())

            user_doc = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "preferences": preferences or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None,
                "active": True,
            }

            self.users_collection.insert_one(user_doc)
            logger.info(f"Created user with ID: {user_id}")
            return user_id

        except DuplicateKeyError:
            logger.error(f"User with ID {user_id} or email {email} already exists")
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        try:
            return self.users_collection.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None

    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user information."""
        try:
            updates["updated_at"] = datetime.utcnow()
            result = self.users_collection.update_one(
                {"user_id": user_id}, {"$set": updates}
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return False

    def update_user_login(self, user_id: str):
        """Update user's last login timestamp."""
        try:
            self.users_collection.update_one(
                {"user_id": user_id}, {"$set": {"last_login": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Failed to update login for user {user_id}: {e}")

    # ============================================================================
    # Session Management Functions
    # ============================================================================

    def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        session_name: Optional[str] = None,
    ) -> str:
        """
        Create a new session.

        Args:
            user_id: ID of the user creating the session
            session_id: Unique session identifier. If None, generates UUID.
            session_name: Human-readable session name

        Returns:
            Session ID of created session
        """
        try:
            session_id = session_id or str(uuid.uuid4())

            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "session_name": session_name
                or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "created_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow(),
                "active": True,
                "cell_design_count": 0,
            }

            self.sessions_collection.insert_one(session_doc)
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id

        except DuplicateKeyError:
            logger.error(f"Session with ID {session_id} already exists")
            raise
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        try:
            session = self.sessions_collection.find_one({"session_id": session_id})
            if session:
                # Update last accessed
                self.sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$set": {"last_accessed": datetime.utcnow()}},
                )
            return session
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """Get all sessions for a user."""
        try:
            query = {"user_id": user_id}
            if active_only:
                query["active"] = True

            return list(
                self.sessions_collection.find(query).sort("last_accessed", DESCENDING)
            )
        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    def update_session(self, session_id: str, updates: Dict) -> bool:
        """Update session information."""
        try:
            updates["last_accessed"] = datetime.utcnow()
            result = self.sessions_collection.update_one(
                {"session_id": session_id}, {"$set": updates}
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    def increment_session_design_count(self, session_id: str):
        """Increment the cell design count for a session."""
        try:
            self.sessions_collection.update_one(
                {"session_id": session_id},
                {
                    "$inc": {"cell_design_count": 1},
                    "$set": {"last_accessed": datetime.utcnow()},
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to increment design count for session {session_id}: {e}"
            )

    # ============================================================================
    # Cell Design Storage Functions
    # ============================================================================

    def _serialize_cell_design(self, cell_design: Union[Dict, CellDesign]) -> Dict:
        """Convert cell design to dictionary for storage."""
        if isinstance(cell_design, dict):
            return cell_design
        else:
            return cell_design.model_dump(by_alias=True, mode="python")

    def _deserialize_cell_design(
        self, cell_design_dict: Dict, form_factor: str
    ) -> Union[Dict, CellDesign]:
        """Convert dictionary back to cell design object."""
        try:
            form_factor_lower = form_factor.lower()
            if "cylindrical" in form_factor_lower:
                return CylindricalCellDesignParameters(**cell_design_dict)
            elif "prismatic" in form_factor_lower:
                return PrismaticCellDesignParameters(**cell_design_dict)
            elif "pouch" in form_factor_lower:
                return PouchCellDesignParameters(**cell_design_dict)
            else:
                return cell_design_dict
        except Exception as e:
            logger.warning(
                f"Failed to deserialize cell design: {e}. Returning as dict."
            )
            return cell_design_dict

    def _create_searchable_fields(
        self, cell_design_dict: Dict, context: str, keywords: List[str]
    ) -> str:
        """Create searchable text field for full-text search."""
        searchable_parts = []

        # Add context and keywords
        if context:
            searchable_parts.append(context)
        searchable_parts.extend(keywords)

        # Add chemistry information
        for electrode_type in [
            "Positive electrode formulation",
            "Negative electrode formulation",
        ]:
            if electrode_type in cell_design_dict:
                formulation = cell_design_dict[electrode_type]
                if isinstance(formulation, dict) and "Name" in formulation:
                    searchable_parts.append(formulation["Name"])
                elif isinstance(formulation, str):
                    searchable_parts.append(formulation)

        # Add form factor
        if "Form factor" in cell_design_dict:
            searchable_parts.append(cell_design_dict["Form factor"])

        # Add dimensions as text
        if (
            "Cell diameter [mm]" in cell_design_dict
            and "Cell height [mm]" in cell_design_dict
        ):
            searchable_parts.append(
                f"{cell_design_dict['Cell diameter [mm]']}{cell_design_dict['Cell height [mm]']}"
            )

        return " ".join(str(part).lower() for part in searchable_parts if part)

    def store_cell_design(
        self,
        cell_design_dict: Dict,
        session_id: str,
        user_id: str,
        cell_design_id: Optional[str] = None,
    ) -> str:
        """
        Store a cell design in MongoDB with new structure.
        The cell_design_dict should contain: design_hash, keywords, context,
        description, created_at, cell_design_parameters, bill_of_materials

        Args:
            cell_design_dict: Complete cell design dictionary with all fields
            session_id: Session identifier (required)
            user_id: User identifier (required)
            cell_design_id: Unique cell design ID. If None, generates UUID.

        Returns:
            Cell design ID of the stored design
        """
        try:
            # Generate unique cell design ID
            cell_design_id = cell_design_id or str(uuid.uuid4())

            # Prepare document for storage with new structure
            document = {
                "cell_design_id": cell_design_id,
                "session_id": session_id,
                "user_id": user_id,
                "cell_design": cell_design_dict,
            }

            # Store in MongoDB
            try:
                self.cell_designs_collection.insert_one(document)

                # Update session design count
                self.increment_session_design_count(session_id)

                logger.info(
                    f"Successfully stored cell design with ID: {cell_design_id}"
                )
                return cell_design_id

            except DuplicateKeyError:
                logger.error(f"Cell design with ID {cell_design_id} already exists")
                raise ValueError(f"Cell design with ID {cell_design_id} already exists")

        except Exception as e:
            logger.error(f"Failed to store cell design: {e}")
            raise

    def fetch_cell_design(self, cell_design_id: str) -> Optional[dict]:
        """
        Fetch a cell design by its ID.

        Args:
            cell_design_id: Unique ID of the cell design

        Returns:
            dict if found, None otherwise
        """
        try:
            document = self.cell_designs_collection.find_one(
                {"cell_design_id": cell_design_id}
            )

            if not document:
                return None

            logger.info(f"Successfully fetched cell design with ID: {cell_design_id}")
            return document

        except Exception as e:
            logger.error(f"Failed to fetch cell design with ID {cell_design_id}: {e}")
            return None

    # ============================================================================
    # Advanced Search Functions
    # ============================================================================

    def search_cell_designs(
        self,
        search_query: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        design_hash: Optional[str] = None,
        context: Optional[str] = None,
        description: Optional[str] = None,
        cell_design_filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "cell_design.created_at",
        sort_order: int = -1,
    ) -> List[Dict]:
        """
        Advanced search for cell designs with new structure.

        Args:
            search_query: Full-text search query
            keywords: List of keywords to match
            user_id: Filter by user ID
            session_id: Filter by session ID
            design_hash: Filter by design hash
            context: Filter by context
            description: Filter by description
            cell_design_filters: Dict with filters for cell_design_parameters fields
            limit: Maximum results to return
            offset: Number of results to skip
            sort_by: Field to sort by
            sort_order: 1 for ascending, -1 for descending

        Returns:
            List of cell design documents
        """
        try:
            # Build query
            query = {}

            # Text search
            if search_query:
                query["$text"] = {"$search": search_query}

            # User and session filters
            if user_id:
                query["user_id"] = user_id
            if session_id:
                query["session_id"] = session_id

            # Cell design field filters
            if design_hash:
                query["cell_design.design_hash"] = design_hash

            if keywords:
                query["cell_design.keywords"] = {"$in": keywords}

            if context:
                query["cell_design.context"] = {"$regex": context, "$options": "i"}

            if description:
                query["cell_design.description"] = {
                    "$regex": description,
                    "$options": "i",
                }

            # Cell design parameters filters
            if cell_design_filters:
                for key, value in cell_design_filters.items():
                    if isinstance(value, dict):
                        # Range queries like {"$gte": 1, "$lte": 10}
                        query[f"cell_design.cell_design_parameters.{key}"] = value
                    elif isinstance(value, str):
                        # String matching with regex
                        query[f"cell_design.cell_design_parameters.{key}"] = {
                            "$regex": value,
                            "$options": "i",
                        }
                    else:
                        query[f"cell_design.cell_design_parameters.{key}"] = value

            # Execute query with sorting and pagination
            cursor = (
                self.cell_designs_collection.find(query)
                .sort(sort_by, sort_order)
                .skip(offset)
                .limit(limit)
            )

            results = list(cursor)
            logger.info(f"Found {len(results)} cell designs matching search criteria")
            return results

        except Exception as e:
            logger.error(f"Failed to search cell designs: {e}")
            return []

    def search_cell_designs_by_key_value(
        self,
        key_value_pairs: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        search_in_parameters: bool = True,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Search cell designs by specific key-value pairs.

        Args:
            key_value_pairs: Dict of field -> value pairs
            user_id: Filter by user ID
            session_id: Filter by session ID
            search_in_parameters: If True, search in cell_design_parameters, else in top-level cell_design
            limit: Maximum results to return

        Returns:
            List of matching cell design documents
        """
        try:
            # Build query
            query = {}

            # Add user/session filters
            if user_id:
                query["user_id"] = user_id
            if session_id:
                query["session_id"] = session_id

            # Add key-value pair filters
            for key, value in key_value_pairs.items():
                field_path = (
                    f"cell_design.cell_design_parameters.{key}"
                    if search_in_parameters
                    else f"cell_design.{key}"
                )

                if isinstance(value, str):
                    # Case-insensitive string matching
                    query[field_path] = {"$regex": value, "$options": "i"}
                elif isinstance(value, (int, float)):
                    # Exact numeric matching
                    query[field_path] = value
                elif isinstance(value, dict):
                    # Range or complex queries
                    query[field_path] = value
                else:
                    query[field_path] = value

            # Execute query
            cursor = (
                self.cell_designs_collection.find(query)
                .sort("cell_design.created_at", -1)
                .limit(limit)
            )

            results = list(cursor)
            logger.info(f"Found {len(results)} cell designs matching key-value pairs")
            return results

        except Exception as e:
            logger.error(f"Failed to search by key-value pairs: {e}")
            return []

    def search_cell_designs_by_design_hash(
        self,
        design_hash: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Search cell designs by design_hash stored in cell_design.

        Args:
            design_hash: The design hash to search for
            user_id: Optional filter by user ID
            session_id: Optional filter by session ID
            limit: Maximum results to return

        Returns:
            List of matching cell design documents
        """
        try:
            # Build query
            query = {"cell_design.design_hash": design_hash}

            # Add user/session filters
            if user_id:
                query["user_id"] = user_id
            if session_id:
                query["session_id"] = session_id

            # Execute query
            cursor = (
                self.cell_designs_collection.find(query)
                .sort("cell_design.created_at", -1)
                .limit(limit)
            )

            results = list(cursor)
            logger.info(
                f"Found {len(results)} cell designs with design_hash: {design_hash}"
            )
            return results

        except Exception as e:
            logger.error(f"Failed to search by design_hash {design_hash}: {e}")
            return []

    def search_cell_designs_by_bill_of_materials(
        self,
        bom_filters: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Search cell designs by bill of materials fields.

        Args:
            bom_filters: Dict of bill_of_materials field -> value pairs
            user_id: Filter by user ID
            session_id: Filter by session ID
            limit: Maximum results to return

        Returns:
            List of matching cell design documents
        """
        try:
            # Build query
            query = {}

            # Add user/session filters
            if user_id:
                query["user_id"] = user_id
            if session_id:
                query["session_id"] = session_id

            # Add bill of materials filters
            for key, value in bom_filters.items():
                if isinstance(value, str):
                    # Case-insensitive string matching
                    query[f"cell_design.bill_of_materials.{key}"] = {
                        "$regex": value,
                        "$options": "i",
                    }
                elif isinstance(value, (int, float)):
                    # Exact numeric matching
                    query[f"cell_design.bill_of_materials.{key}"] = value
                elif isinstance(value, dict):
                    # Range or complex queries
                    query[f"cell_design.bill_of_materials.{key}"] = value
                else:
                    query[f"cell_design.bill_of_materials.{key}"] = value

            # Execute query
            cursor = (
                self.cell_designs_collection.find(query)
                .sort("cell_design.created_at", -1)
                .limit(limit)
            )

            results = list(cursor)
            logger.info(f"Found {len(results)} cell designs matching BOM criteria")
            return results

        except Exception as e:
            logger.error(f"Failed to search by bill of materials: {e}")
            return []

    def get_user_cell_designs(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """
        Get all cell designs for a user, optionally filtered by session.

        Args:
            user_id: User ID to filter by
            session_id: Optional session filter
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of cell design documents
        """
        try:
            # Build query
            query = {"user_id": user_id}
            if session_id:
                query["session_id"] = session_id

            # Execute query
            cursor = (
                self.cell_designs_collection.find(query)
                .sort("cell_design.created_at", -1)
                .skip(offset)
                .limit(limit)
            )

            results = list(cursor)
            logger.info(f"Fetched {len(results)} cell designs for user {user_id}")
            return results

        except Exception as e:
            logger.error(f"Failed to fetch cell designs for user {user_id}: {e}")
            return []

    def get_session_cell_designs(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """
        Get all cell designs for a session.

        Args:
            session_id: Session ID to filter by
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of cell design documents
        """
        try:
            query = {"session_id": session_id}
            cursor = (
                self.cell_designs_collection.find(query)
                .sort("cell_design.created_at", -1)
                .skip(offset)
                .limit(limit)
            )

            results = list(cursor)
            logger.info(f"Fetched {len(results)} cell designs for session {session_id}")
            return results

        except Exception as e:
            logger.error(f"Failed to fetch cell designs for session {session_id}: {e}")
            return []

    def update_cell_design(
        self,
        cell_design_id: str,
        context: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> bool:
        """
        Update fields within the cell_design object.

        Args:
            cell_design_id: ID of the cell design to update
            context: New context description
            keywords: New keywords list
            description: New description

        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Build update document for nested fields
            update_doc = {}

            if context is not None:
                update_doc["cell_design.context"] = context

            if keywords is not None:
                update_doc["cell_design.keywords"] = keywords

            if description is not None:
                update_doc["cell_design.description"] = description

            if not update_doc:
                logger.warning("No fields to update")
                return False

            # Update document
            result = self.cell_designs_collection.update_one(
                {"cell_design_id": cell_design_id}, {"$set": update_doc}
            )

            if result.matched_count == 0:
                logger.warning(f"No cell design found with ID: {cell_design_id}")
                return False

            logger.info(f"Successfully updated cell design with ID: {cell_design_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update cell design with ID {cell_design_id}: {e}")
            return False

    def delete_cell_design(self, cell_design_id: str) -> bool:
        """
        Delete a cell design from the database.

        Args:
            cell_design_id: ID of the cell design to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Get the design to know which session to update
            design_doc = self.cell_designs_collection.find_one(
                {"cell_design_id": cell_design_id}
            )

            result = self.cell_designs_collection.delete_one(
                {"cell_design_id": cell_design_id}
            )

            if result.deleted_count == 0:
                logger.warning(f"No cell design found with ID: {cell_design_id}")
                return False

            # Decrement session design count
            if design_doc and "session_id" in design_doc:
                self.sessions_collection.update_one(
                    {"session_id": design_doc["session_id"]},
                    {"$inc": {"cell_design_count": -1}},
                )

            logger.info(f"Successfully deleted cell design with ID: {cell_design_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete cell design with ID {cell_design_id}: {e}")
            return False

    def clear_all_cell_designs(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear all cell designs from the database, optionally filtered by user.

        Args:
            user_id: Optional user ID to clear designs for specific user only.
                     If None, clears all designs for all users.

        Returns:
            Dictionary with deletion results and statistics
        """
        try:
            # Build query filter
            query_filter = {}
            if user_id:
                query_filter["user_id"] = user_id

            # Get count before deletion for reporting
            total_designs = self.cell_designs_collection.count_documents(query_filter)
            
            if total_designs == 0:
                return {
                    "success": True,
                    "message": f"No cell designs found{' for user' if user_id else ''}",
                    "deleted_count": 0,
                    "user_id": user_id
                }

            # Get all designs to be deleted for session updates
            designs_to_delete = list(self.cell_designs_collection.find(
                query_filter, 
                {"cell_design_id": 1, "session_id": 1}
            ))

            # Delete all matching designs
            result = self.cell_designs_collection.delete_many(query_filter)
            deleted_count = result.deleted_count

            # Update session counts
            session_updates = {}
            for design in designs_to_delete:
                session_id = design.get("session_id")
                if session_id:
                    if session_id not in session_updates:
                        session_updates[session_id] = 0
                    session_updates[session_id] += 1

            # Apply session count updates
            for session_id, count_decrease in session_updates.items():
                self.sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$inc": {"cell_design_count": -count_decrease}},
                )

            # Reset any negative counts to 0
            self.sessions_collection.update_many(
                {"cell_design_count": {"$lt": 0}},
                {"$set": {"cell_design_count": 0}}
            )

            message = f"Successfully cleared {deleted_count} cell designs"
            if user_id:
                message += f" for user {user_id}"
            else:
                message += " for all users"

            logger.info(message)
            
            return {
                "success": True,
                "message": message,
                "deleted_count": deleted_count,
                "user_id": user_id,
                "sessions_updated": len(session_updates)
            }

        except Exception as e:
            error_msg = f"Failed to clear cell designs{' for user' if user_id else ''}: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "deleted_count": 0,
                "user_id": user_id
            }

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.

        Returns:
            Dictionary with database statistics
        """
        try:
            stats = {}

            # Collection stats
            stats["users"] = {
                "count": self.users_collection.count_documents({}),
                "active_users": self.users_collection.count_documents({"active": True}),
            }

            stats["sessions"] = {
                "count": self.sessions_collection.count_documents({}),
                "active_sessions": self.sessions_collection.count_documents(
                    {"active": True}
                ),
            }

            stats["cell_designs"] = {
                "count": self.cell_designs_collection.count_documents({})
            }

            # Form factor distribution
            form_factor_pipeline = [
                {"$group": {"_id": "$form_factor", "count": {"$sum": 1}}}
            ]
            stats["form_factor_distribution"] = list(
                self.cell_designs_collection.aggregate(form_factor_pipeline)
            )

            # # Chemistry distribution
            # chemistry_pipeline = [
            #     {
            #         "$group": {
            #             "_id": "$metadata.positive_chemistry",
            #             "count": {"$sum": 1},
            #         }
            #     }
            # ]
            # stats["chemistry_distribution"] = list(
            #     self.cell_designs_collection.aggregate(chemistry_pipeline)
            # )

            # Recent activity
            stats["designs_last_24h"] = self.cell_designs_collection.count_documents(
                {
                    "created_at": {
                        "$gte": datetime.utcnow().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                    }
                }
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    # ============================================================================
    # Utility Functions
    # ============================================================================

    def get_or_create_default_user(self, user_id: str = "default_user") -> str:
        """Get or create a default user for testing/demo purposes."""
        try:
            user = self.get_user(user_id)
            if not user:
                return self.create_user(
                    user_id=user_id,
                    name="Default User",
                    preferences={"theme": "light", "units": "metric"},
                )
            return user_id
        except Exception as e:
            logger.error(f"Failed to get/create default user: {e}")
            raise

    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old inactive sessions and their associated data."""
        try:
            cutoff_date = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date - timedelta(days=days_old)

            # Find old inactive sessions
            old_sessions = list(
                self.sessions_collection.find(
                    {"active": False, "last_accessed": {"$lt": cutoff_date}}
                )
            )

            session_ids = [session["session_id"] for session in old_sessions]

            if session_ids:
                # Delete associated cell designs
                designs_result = self.cell_designs_collection.delete_many(
                    {"session_id": {"$in": session_ids}}
                )

                # Delete sessions
                sessions_result = self.sessions_collection.delete_many(
                    {"session_id": {"$in": session_ids}}
                )

                logger.info(
                    f"Cleaned up {sessions_result.deleted_count} old sessions "
                    f"and {designs_result.deleted_count} associated cell designs"
                )

                return {
                    "sessions_deleted": sessions_result.deleted_count,
                    "designs_deleted": designs_result.deleted_count,
                }

            return {"sessions_deleted": 0, "designs_deleted": 0}

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {"error": str(e)}


# Global instance for easy access
_mongodb_storage: Optional[MongoDBCellDesignStorage] = None


def get_mongodb_storage() -> MongoDBCellDesignStorage:
    """Get or create the global MongoDB storage instance."""
    global _mongodb_storage
    if _mongodb_storage is None:
        _mongodb_storage = MongoDBCellDesignStorage()
    return _mongodb_storage


def close_mongodb_storage():
    """Close the global MongoDB storage connection."""
    global _mongodb_storage
    if _mongodb_storage:
        _mongodb_storage.close_connection()
        _mongodb_storage = None
