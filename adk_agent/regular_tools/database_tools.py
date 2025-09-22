"""
Database Tools - Regular Python functions converted from MCP tools
"""

import hashlib
import json
import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from google.adk.tools.function_tool import FunctionTool

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_server.cell_designer.mongodb_interface import get_mongodb_storage
from mcp_server.tools import extract_keywords_from_parameters, generate_context_description


def store_cell_design_in_db(
    cell_design: dict,
    user_id: str,
    session_id: Optional[str] = None,
) -> dict:
    """
    Store a cell design in the database.

    Args:
        cell_design: The cell design dictionary to store
        user_id: User ID for the design
        session_id: Optional session ID (creates new session if None)

    Returns:
        Dictionary with storage status and design hash ID
    """
    try:
        storage = get_mongodb_storage()

        # Create session if none provided
        if not session_id:
            session_id = storage.create_session(
                user_id=user_id,
                session_name=f"Cell Design Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            )

        # The cell_design already comes in the correct structure from get_cell_design
        # Just ensure all required fields are present with fallbacks

        if "design_hash" not in cell_design:
            params = cell_design.get("cell_design_parameters", {})
            design_str = json.dumps(params, sort_keys=True, default=str)
            cell_design["design_hash"] = hashlib.md5(design_str.encode()).hexdigest()[:8]

        if "keywords" not in cell_design:
            cell_design["keywords"] = []

        if "context" not in cell_design:
            cell_design["context"] = "Cell design created via get_cell_design"

        if "description" not in cell_design:
            cell_design["description"] = "Auto-generated cell design"

        if "created_at" not in cell_design:
            cell_design["created_at"] = datetime.now(timezone.utc).isoformat()

        if "bill_of_materials" not in cell_design:
            cell_design["bill_of_materials"] = {}

        if "cell_design_parameters" not in cell_design:
            cell_design["cell_design_parameters"] = {}

        design_id = storage.store_cell_design(
            cell_design_dict=cell_design,
            session_id=session_id,
            user_id=user_id,
        )

    except Exception as e:
        return {"status": "failed", "message": f"Failed to store cell design: {str(e)}"}
    
    return {
        "status": "success",
        "cell_design_id": design_id,
        "message": "Cell design stored successfully",
    }


def search_cell_designs_in_db(
    user_id: str,
    design_id: Optional[str] = None,
    design_hash: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    context: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    Search for cell designs in the database. Users can only search their own designs.

    Args:
        user_id: User ID for the search
        design_id: Specific design ID to search for
        design_hash: Specific design hash to search for
        keywords: List of keywords to match
        context: Context text to search for
        limit: Maximum number of results

    Returns:
        Dictionary with search results containing design hash IDs
    """
    try:
        storage = get_mongodb_storage()

        # If searching by specific design ID
        if design_id:
            design_doc = storage.fetch_cell_design(design_id)
            if design_doc and design_doc.get("user_id") == user_id:
                return {
                    "status": "success",
                    "results": [design_id],
                    "total_found": 1,
                    "message": "Design found",
                }
            else:
                return {"status": "failed", "message": "Design not found or access denied"}

        # General search with new structure
        results = storage.search_cell_designs(
            user_id=user_id,  # Only search user's designs
            keywords=keywords,
            context=context,
            design_hash=design_hash,
            limit=limit,
        )

        # Extract design IDs
        design_ids = [result["cell_design_id"] for result in results]

    except Exception as e:
        return {"status": "failed", "message": f"Search failed: {str(e)}"}

    return {
        "status": "success",
        "results": design_ids,
        "total_found": len(design_ids),
        "message": f"Found {len(design_ids)} designs",
    }


def fetch_cell_design_from_db(
    cell_design_id: str,
    user_id: str,
    include_simulations: bool = True,
) -> dict:
    """
    Fetch a cell design from the database.

    Args:
        cell_design_id: ID of the cell design to fetch
        user_id: User ID for access control
        include_simulations: Whether to include simulation results

    Returns:
        Dictionary with cell design data or error message
    """
    try:
        storage = get_mongodb_storage()
        design_doc = storage.fetch_cell_design(cell_design_id)
        
        if not design_doc:
            return {"status": "failed", "message": "Design not found"}
            
        if design_doc.get("user_id") != user_id:
            return {"status": "failed", "message": "Access denied"}
        
        return {
            "status": "success",
            "cell_design": design_doc,
            "message": "Design retrieved successfully"
        }
        
    except Exception as e:
        return {"status": "failed", "message": f"Failed to fetch design: {str(e)}"}


def list_user_sessions_in_db(user_id: str, limit: int = 50) -> dict:
    """
    List all sessions for a user.

    Args:
        user_id: User ID
        limit: Maximum number of sessions to return

    Returns:
        Dictionary with session list or error message
    """
    try:
        storage = get_mongodb_storage()
        sessions = storage.list_user_sessions(user_id=user_id, limit=limit)
        
        return {
            "status": "success",
            "sessions": sessions,
            "total_found": len(sessions),
            "message": f"Found {len(sessions)} sessions"
        }
        
    except Exception as e:
        return {"status": "failed", "message": f"Failed to list sessions: {str(e)}"}


def delete_cell_design_from_db(cell_design_id: str, user_id: str) -> dict:
    """
    Delete a cell design from the database.

    Args:
        cell_design_id: ID of the cell design to delete
        user_id: User ID for access control

    Returns:
        Dictionary with deletion status
    """
    try:
        storage = get_mongodb_storage()
        
        # First check if design exists and belongs to user
        design_doc = storage.fetch_cell_design(cell_design_id)
        if not design_doc:
            return {"status": "failed", "message": "Design not found"}
            
        if design_doc.get("user_id") != user_id:
            return {"status": "failed", "message": "Access denied"}
        
        # Delete the design
        success = storage.delete_cell_design(cell_design_id)
        
        if success:
            return {
                "status": "success",
                "message": "Cell design deleted successfully"
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to delete cell design"
            }
        
    except Exception as e:
        return {"status": "failed", "message": f"Failed to delete design: {str(e)}"}


# Create FunctionTool wrappers for ADK
store_cell_design_in_db_tool = FunctionTool(store_cell_design_in_db)
search_cell_designs_in_db_tool = FunctionTool(search_cell_designs_in_db)
fetch_cell_design_from_db_tool = FunctionTool(fetch_cell_design_from_db)
list_user_sessions_in_db_tool = FunctionTool(list_user_sessions_in_db)
delete_cell_design_from_db_tool = FunctionTool(delete_cell_design_from_db)