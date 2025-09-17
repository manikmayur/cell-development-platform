"""
Battery Cell Designer Co-pilot

This module provides functionality for exploring different cell form factors and chemistries by creating cell designs.
It also has the capability to store and retrieve these designs for future use using a database management system.
It also simulates battery cell performance under various conditions using the thermally coupled P2D model.

One can estimate Capacity, Energy, Maximum Power, and DCIR at different temperatures and state-of-charge.
One can also perform gap analysis of a certain cell design against a target specification.
It can also be used to predict the chemistry of a battery cell based on its characteristics.
"""

import hashlib
import logging
import json
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pybamm
import uvicorn
import signal
import functools
from mcp.server.fastmcp import FastMCP
from typing import (
    Optional,
    List,
)
import sys
import os
import rdp
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

from mcp_server.cell_designer.cell_design import CellDesign, POSITIVE_ELECTRODE_MASS_LOADING_MIN, POSITIVE_ELECTRODE_MASS_LOADING_MAX
from mcp_server.cell_designer.electrode_formulation import KNOWN_FORMULATIONS, ElectrodeFormulation
from mcp_server.cell_designer.mongodb_interface import (
    get_mongodb_storage,
)
from mcp_server.tools import (
    extract_keywords_from_parameters,
    generate_context_description,
)
from dotenv import load_dotenv

# Configure logging to suppress authentication warnings
logging.basicConfig(level=logging.INFO)
# Suppress all MCP-related warnings aggressively
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
logging.getLogger("mcp.server.base_authenticated_tool").setLevel(logging.ERROR)
logging.getLogger("mcp.server.auth").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Set environment variables to disable authentication warnings
os.environ["MCP_DISABLE_AUTH"] = "1"
# Also try to suppress warnings at the system level
# warnings.filterwarnings("ignore", category=UserWarning, module="mcp")

load_dotenv(dotenv_path="../../.env")

# Initialize FastMCP server
mcp = FastMCP("cell-design-mcp")

# Timeout decorator for long-running operations
def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def with_timeout(timeout_seconds):
    """Decorator to add timeout to functions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set up timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Clean up timeout
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        return wrapper
    return decorator

# Get timeout from environment variable
TOOL_TIMEOUT = int(os.getenv("MCP_TOOL_TIMEOUT", "3600"))  # 60 minutes default

TOOL_INFO_FOOTER = (
    """*Always* accompany the results with a precise account of the limitations of the model.
    *Always* refer to the results of the tools to answer factual questions.
    *Always* cite a reference/source for the facts and interpretations when any tool is not used.
    *Always* check the results for correctness and reasonableness.
    But omit mentioning tool errors. Provide quantitative relative errors when you can."""
)

# Global list of valid cell design parameter aliases
# To add nested dict attributes (e.g., keys inside "Negative electrode formulation" or "Positive electrode formulation"),
# you can use dot notation or another convention to represent nested fields as strings.
# For example, "Negative electrode formulation.Name", "Positive electrode formulation.Primary binder", etc.

VALID_CELL_DESIGN_ALIASES = [
    "Form factor",
    "Positive electrode mass loading [mg.cm-2]",
    "Positive electrode sheet count",
    "Positive electrode coating thickness [um]",
    "Positive electrode foil thickness [um]",
    "Negative electrode mass loading [mg.cm-2]",
    "Negative electrode coating thickness [um]",
    "Negative electrode foil thickness [um]",
    "Negative electrode formulation",
    "Positive electrode formulation",
    "Separator thickness [um]",
    "Separator areal density [g.m-2]",
    "Cell height [mm]",
    "Cell diameter [mm]",
    "Cell width [mm]",
    "Cell thickness [mm]",
    "Cell volume packing ratio",
    "Cell mass packing ratio",
    "Cell electrode overhang [mm]",
    "Cell casing thickness [mm]",
    "Cell casing material",
    "Cell thermal resistance [K.W-1]",
    "Cell cooling arc [degree]",
    "Cell cooling channel height [mm]",
    "Jelly roll inner diameter [mm]",
    "Jelly roll count",
    "Upper voltage cut-off [V]",
    "Lower voltage cut-off [V]",
    # Nested dict attributes (dot notation)
    # "Negative electrode formulation.Name",
    "Negative electrode formulation.Primary binder",
    "Negative electrode formulation.Secondary binder",
    "Negative electrode formulation.Primary active material",
    "Negative electrode formulation.Primary binder mass fraction",
    "Negative electrode formulation.Secondary binder mass fraction",
    "Negative electrode formulation.Electrode specific capacity [mAh.g-1]",
    "Negative electrode formulation.Primary active material mass fraction",
    # "Positive electrode formulation.Name",
    "Positive electrode formulation.Primary binder",
    "Positive electrode formulation.Primary active material",
    "Positive electrode formulation.Primary conductive agent",
    "Positive electrode formulation.Primary binder mass fraction",
    "Positive electrode formulation.Electrode specific capacity [mAh.g-1]",
    "Positive electrode formulation.Primary active material mass fraction",
    "Positive electrode formulation.Primary conductive agent mass fraction",
    # Add Can material attributes if needed
    "Cell casing material.Name",
    "Cell casing material.Specific heat capacity [J.kg-1.K-1]",
    "Cell casing material.Density [g.cm-3]",
    "Cell casing material.Thermal conductivity [W.m-1.K-1]",
    # ...add more nested keys as needed...
]

# =========================================================================
# Workflows Help Information
# =========================================================================
@mcp.tool()
def workflows_help_info() -> str:
    """
    Is queried when the user asks for help or information about how the copilot can be used.
    Returns a list of workflows.
    """
    return (
        "Return this list to the user:\n"
        "- **Cell Design Workflow**: Use this workflow to design a battery cell with specific parameters and tradeoffs.\n"
        "- **Materials Workflow**: Use this workflow to find and rank cathode materials based on their properties.\n"
        "- **Simulation Workflow**: Use this workflow to simulate the performance of a battery cell under different conditions.\n"
        "- **Literature Search Workflow**: Use this workflow to search for scientific literature related to battery materials and cell design.\n"
        "Of course, we can mix and match these workflows as needed to answer your questions.\n"
    )

@mcp.tool()
def prepare_cell_design_workflow() -> str:
    """
    This tool is always queried first when the user inquires about cell design capabilities, or
    using cell design tools is being considered by the agent, in order to provide context about the
    cell design tools available in the MCP environment, and how to use them. 
    *DO NOT* perform any calculations by yourself Unless specifically asked to do so.
    *Always* use the tools to perform the calculations.
    *Always* be explicit in highlighting which information is verfied and which is not.

    """
    return (
        "When designing a cell, focus on the tradeoffs between performance, cost, manufacturability, and safety."
        "If trying to generate a cell design, first confirm cell dimensions and electrode formulations, always make at least 3 propositions, and render performance, cost, manufacturability, and safety tradeoffs in a radar chart."
        "Work with reasonable tradeoffs and up to 1% tolerances in design targets."
    )

@mcp.tool()
def prepare_simulation_workflow() -> str:
    """
    This tool is always queried first when the user inquires about simulation capabilities, or
    using simulation tools is being considered by the agent, in order to provide context about the
    simulation tools available in the MCP environment, and how to use them.
    *ALWAYS* calibrate contact resistance using given power, dcir, and energy at 25degC as reference before comparing to user provided power, dcir, and energy.
    *DO NOT* perform any calculations by yourself Unless specifically asked to do so.
    *Always* use the tools to perform the calculations.
    *Always* be explicit in highlighting which information is verfied and which is not.
    """
    return (
        """
        - Before simulating cell performance, search for model parameters and similar results in the database.
        - If a similar result is found, load and set the appropriate cell model from database.
        -*Always* calibrate contact resistance using given power, dcir, and energy at 25degC as reference before comparing to user provided power, dcir, and energy."""
    )

@mcp.tool()
def finalize_answer() -> str:
    """
    This tool should always be called before presenting a final answer. Double-checks reasoning, calculations, and logic.
    Use this tool after completing your chain of thought to ensure the answer is robust and free of errors.
    *DO NOT* perform any calculations by yourself Unless specifically asked to do so.
    *Always* use the tools to perform the calculations.
    *Always* be explicit in highlighting which information is verfied and which is not.
    """
    return (
        "Guidelines:"
        "Go back over the previous reasoning steps and check the following:"
        "- Review all calculations for correctness (units, formulas, edge cases)."
        "- Ensure all assumptions are stated and reasonable."
        "- Check that the answer directly addresses the user's question."
        "- If any uncertainty remains, state it clearly."
        "- If any concept or fact has been mentioned from memory, verify it using web search, or state that it is not verified."
        "- If relevant, suggest next steps for further validation or testing."
        "- Criticize performance, cost, manufacturability, and safety tradeoffs of the proposed cell design."
    )

@mcp.tool()
def visualization_guidelines() -> dict:
    """
    Provides guidelines for generating visualizations in the MCP environment.
    This tool should be called every time a visualization is generated to ensure
    that the output is compatible with the MCP Preview tab.
    """
    return {
        "description": (
            "Visualization Guidelines for MCP Environment:\n\n"
            "1. **Primary Format**: Generate all visualizations as HTML files (text/html type) with embedded JavaScript for interactivity. Do not use React.\n\n"
            "2. **Interactive Features** (if relevant): Use vanilla JavaScript or import libraries from https://cdnjs.cloudflare.com to create:\n"
            "   - Hover tooltips showing data values\n"
            "   - Zoom and pan functionality\n"
            "   - Toggle data series on/off\n"
            "   - Responsive resizing\n"
            "   - Real-time parameter adjustment with sliders/inputs (if relevant)\n\n"
            "3. **Recommended Libraries** (via CDN):\n"
            "   - Chart.js for interactive charts\n"
            "   - D3.js for custom visualizations\n"
            "   - Plotly.js for scientific/engineering plots\n"
            "   - Canvas API for custom plotting when libraries aren't suitable\n"
        )
    }

# =========================================================================
# Database Interaction Tools
# =========================================================================

@mcp.tool()
def store_cell_design_in_db(
    cell_design: dict,
    user_id: Optional[str],
    session_id: Optional[str] = None,
) -> dict:
    """
    Store a cell design in the database.

    Args:
        cell_design: The cell design dictionary to store
        user_id: Automatically set by the MCP server
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
            cell_design["design_hash"] = hashlib.md5(design_str.encode()).hexdigest()[
                :8
            ]

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

@mcp.tool()
def search_cell_designs_in_db(
    user_id: Optional[str],
    design_id: Optional[str] = None,
    design_hash: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    context: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    Search for cell designs in the database. Users can only search their own designs.

    Args:
        user_id: Automatically set by the MCP server
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

@mcp.tool()
def fetch_cell_design_from_db(
    cell_design_id: str,
    user_id: Optional[str],
    include_simulations: bool = True,
    simulation_type: str = None,
) -> dict:
    """
    Fetch a cell design from database by its hash ID.
    Enhanced to optionally include simulation results and filter by simulation type.

    Args:
        user_id: Automatically set by the MCP server
        cell_design_id: Hash ID of the design to fetch
        include_simulations (bool): Whether to include simulation results (default: True)
        simulation_type (str): Specific simulation type to include (optional)

    Returns:
        Dictionary with the cell design data or error
    """
    try:
        storage = get_mongodb_storage()

        # Get the design document directly to check ownership
        design_doc = storage.cell_designs_collection.find_one(
            {"cell_design_id": cell_design_id}
        )

        if not design_doc:
            return {"status": "failed", "message": f"No design found with ID: {cell_design_id}"}

        # Check if user owns this design
        if design_doc.get("user_id") != user_id:
            return {"status": "failed", "message": "Access denied - you can only access your own designs"}

        # Return the cell design data
        cell_design = design_doc["cell_design"].copy()
        
        # Enhanced simulation handling (merged helper functions)
        if include_simulations and "simulation_results" in cell_design:
            simulation_results = cell_design["simulation_results"]
            
            if simulation_type:
                # Standardize the requested type
                type_mapping = {
                    "Power": "Power_performance",
                    "Power performance": "Power_performance", 
                    "C_rate": "C_rate_performance",
                    "C_rate performance": "C_rate_performance",
                    "DCIR": "DCIR_performance",
                    "DCIR performance": "DCIR_performance"
                }
                requested_type = type_mapping.get(simulation_type, simulation_type)
                
                if requested_type in simulation_results:
                    cell_design["simulation_results"] = {
                        requested_type: simulation_results[requested_type]
                    }
                else:
                    return {"status": "failed", "message": f"No {requested_type} simulation results found", "cell_design": cell_design}
            # If no simulation_type specified, include all simulations
        elif not include_simulations:
            # Remove simulation data if not requested
            cell_design.pop("simulation_results", None)
            cell_design.pop("simulation_history", None)

        return {
            "status": "success",
            "cell_design": cell_design,
            "message": "Design fetched successfully",
            "includes_simulations": include_simulations and "simulation_results" in cell_design,
            "simulation_count": len(cell_design.get("simulation_results", {}))
        }

    except Exception as e:
        return {"status": "failed", "message": f"Failed to fetch design: {str(e)}", "cell_design": cell_design}

@mcp.tool()
def get_cell_design_inventory_from_db(user_id: Optional[str]) -> dict:
    """
    Get an inventory of all cell designs stored for a specific user.

    Args:
        user_id: Automatically set by the MCP server

    Returns:
        Dictionary with inventory of user's designs
    """
    try:
        storage = get_mongodb_storage()

        # Get all designs for the user
        designs = storage.get_user_cell_designs(user_id=user_id, limit=100)

        # Create inventory
        inventory = {
            "total_designs": len(designs),
            "form_factors": {},
            "recent_designs": [],
            "sessions": {},
        }

        def parse_datetime(dt):
            """Helper function to parse datetime from string or return datetime object."""
            if isinstance(dt, str):
                try:
                    return datetime.fromisoformat(dt.replace("Z", "+00:00"))
                except ValueError:
                    return None
            elif isinstance(dt, datetime):
                return dt
            return None

        for design in designs:
            cell_design_data = design.get("cell_design", {})
            cell_design_params = cell_design_data.get("cell_design_parameters", {})

            # Count form factors from nested structure
            form_factor = cell_design_params.get("Form factor", "unknown")
            inventory["form_factors"][form_factor] = (
                inventory["form_factors"].get(form_factor, 0) + 1
            )

            # Track sessions
            session_id = design.get("session_id")
            if session_id:
                created_at_raw = cell_design_data.get("created_at")
                created_at = parse_datetime(created_at_raw)
                if created_at and session_id not in inventory["sessions"]:
                    inventory["sessions"][session_id] = {
                        "count": 0,
                        "latest": created_at,
                    }
                inventory["sessions"][session_id]["count"] += 1
                if created_at:
                    latest_dt = parse_datetime(
                        inventory["sessions"][session_id]["latest"]
                    )
                    if latest_dt and created_at > latest_dt:
                        inventory["sessions"][session_id]["latest"] = created_at

            # Add to recent designs (top 5)
            if len(inventory["recent_designs"]) < 5:
                context = cell_design_data.get("context", "")
                recent_design = {
                    "cell_design_id": design["cell_design_id"],
                    "context": (
                        context[:100] + "..." if len(context) > 100 else context
                    ),
                    "form_factor": form_factor,
                    "created_at": (
                        cell_design_data.get("created_at").isoformat()
                        if cell_design_data.get("created_at")
                        and hasattr(cell_design_data.get("created_at"), "isoformat")
                        else ""
                    ),
                    "keywords": cell_design_data.get("keywords", []),
                }

                            # Add capacity if available from cell design parameters
            if "Cell nominal capacity [A.h]" in cell_design_params:
                recent_design["capacity"] = cell_design_params[
                    "Cell nominal capacity [A.h]"
                ]

            # Add simulation information if available (merged helper functions)
            simulation_results = cell_design_data.get("simulation_results", {})
            if simulation_results:
                recent_design["simulation_count"] = len(simulation_results)
                recent_design["simulation_types"] = list(simulation_results.keys())
                recent_design["last_simulation"] = cell_design_data.get("last_simulation_type")
                recent_design["last_simulation_timestamp"] = cell_design_data.get("last_simulation_timestamp")
                
                # Add simulation summary if available
                if simulation_results:
                    # Get the most recent simulation for summary
                    latest_sim_type = list(simulation_results.keys())[0]
                    latest_sim = simulation_results[latest_sim_type]
                    conditions = latest_sim.get("simulation_conditions", {})
                    
                    # Create conditions summary (merged helper function)
                    summary_parts = []
                    if "power_W" in conditions:
                        summary_parts.append(f"Power: {conditions['power_W']}W")
                    if "c_rate" in conditions:
                        summary_parts.append(f"C-rate: {conditions['c_rate']}C")
                    if "temperature_K" in conditions:
                        temp_c = conditions['temperature_K'] - 273.15
                        summary_parts.append(f"Temp: {temp_c:.1f}°C")
                    if "direction" in conditions:
                        summary_parts.append(f"Direction: {conditions['direction']}")
                    
                    recent_design["latest_simulation_summary"] = ", ".join(summary_parts) if summary_parts else "Basic conditions"

            inventory["recent_designs"].append(recent_design)

        # Convert session timestamps to ISO format
        for session_data in inventory["sessions"].values():
            session_data["latest"] = session_data["latest"].isoformat()

        return {
            "status": "success",
            "inventory": inventory,
            "message": f"Inventory retrieved for {len(designs)} designs",
        }

    except Exception as e:
        return {"status": "failed", "message": f"Failed to get inventory: {str(e)}", "inventory": inventory}

@mcp.tool()
def update_cell_design_in_db(user_id: Optional[str], cell_design_id: str, updates: dict) -> dict:
    """
    Update a cell design by adding simulation results to its JSON data.

    Args:
        user_id: Automatically set by the MCP server
        cell_design_id: Hash ID of the design to update
        updates: Dictionary of updates to apply to the cell design

    Returns:
        Dictionary with update status
    """
    try:
        storage = get_mongodb_storage()

        # Get the design document
        design_doc = storage.cell_designs_collection.find_one(
            {"cell_design_id": cell_design_id}
        )

        if not design_doc:
            return {"status": "failed", "message": f"No design found with ID: {cell_design_id}"}

        # Check ownership
        if design_doc.get("user_id") != user_id:
            return {"status": "failed", "message": "Access denied - you can only update your own designs"}

        # Add simulation results to the cell design JSON
        updated_cell_design = design_doc["cell_design"].copy()

        # Handle simulation-specific updates with enhanced logic
        if "simulation_results" in updates:
            # Initialize simulation_results if it doesn't exist
            if "simulation_results" not in updated_cell_design:
                updated_cell_design["simulation_results"] = {}
            
            # Initialize simulation_history if it doesn't exist
            if "simulation_history" not in updated_cell_design:
                updated_cell_design["simulation_history"] = []
            
            # Process each simulation type
            for sim_type, sim_data in updates["simulation_results"].items():
                # Standardize simulation type naming (merged helper function)
                type_mapping = {
                    "Power": "Power_performance",
                    "Power performance": "Power_performance", 
                    "C_rate": "C_rate_performance",
                    "C_rate performance": "C_rate_performance",
                    "DCIR": "DCIR_performance",
                    "DCIR performance": "DCIR_performance"
                }
                standardized_type = type_mapping.get(sim_type, sim_type)
                
                # Add timestamp and metadata if not present
                if "timestamp" not in sim_data:
                    sim_data["timestamp"] = datetime.now(timezone.utc).isoformat()
                
                # Add checksum for data integrity (merged helper function)
                if "results" in sim_data and "checksum" not in sim_data:
                    data_string = json.dumps(sim_data["results"], sort_keys=True, default=str)
                    sim_data["checksum"] = hashlib.sha256(data_string.encode()).hexdigest()
                
                # Store simulation results
                updated_cell_design["simulation_results"][standardized_type] = sim_data
                
                # Create conditions summary for history (merged helper function)
                conditions = sim_data.get("simulation_conditions", {})
                summary_parts = []
                if "power_W" in conditions:
                    summary_parts.append(f"Power: {conditions['power_W']}W")
                if "c_rate" in conditions:
                    summary_parts.append(f"C-rate: {conditions['c_rate']}C")
                if "temperature_K" in conditions:
                    temp_c = conditions['temperature_K'] - 273.15
                    summary_parts.append(f"Temp: {temp_c:.1f}°C")
                if "direction" in conditions:
                    summary_parts.append(f"Direction: {conditions['direction']}")
                conditions_summary = ", ".join(summary_parts) if summary_parts else "Basic conditions"
                
                # Add to simulation history
                history_entry = {
                    "simulation_type": standardized_type,
                    "timestamp": sim_data["timestamp"],
                    "conditions_summary": conditions_summary,
                    "status": "stored"
                }
                updated_cell_design["simulation_history"].append(history_entry)
            
            # Update last simulation metadata
            updated_cell_design["last_simulation_type"] = list(updates["simulation_results"].keys())[0]
            updated_cell_design["last_simulation_timestamp"] = datetime.now(timezone.utc).isoformat()

        # Handle general updates (existing logic)
        for key, value in updates.items():
            if key != "simulation_results":  # Skip simulation_results as it's handled above
                if key in updated_cell_design:
                    if isinstance(updated_cell_design[key], dict) and isinstance(
                        value, dict
                    ):
                        updated_cell_design[key].update(value)
                    elif isinstance(updated_cell_design[key], list) and isinstance(
                        value, list
                    ):
                        updated_cell_design[key].extend(value)
                    else:
                        updated_cell_design[key] = value
                else:
                    updated_cell_design[key] = value

        # Update the document
        result = storage.cell_designs_collection.update_one(
            {"cell_design_id": cell_design_id},
            {
                "$set": {
                    "cell_design": updated_cell_design,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        )

        if result.matched_count == 0:
            return {"status": "failed", "message": f"No design found with ID: {cell_design_id}"}

    except Exception as e:
        return {"status": "failed", "message": f"Failed to update design: {str(e)}"}
    
    return {
            "status": "success",
            "updated_fields": list(updates.keys()),
            "message": "Design updated with simulation results",
        }

@mcp.tool()
def clear_all_cell_designs(user_id: Optional[str] = None) -> dict:
    """
    Clear all cell designs from the database.
    
    This tool allows you to clear all stored cell designs from the database.
    You can optionally specify a user_id to clear designs for a specific user only.
    If no user_id is provided, it will clear designs for all users.
    
    WARNING: This operation is irreversible and will permanently delete all cell designs!
    
    Args:
        user_id: Optional user ID to clear designs for specific user only.
                 If None, clears all designs for all users.
    
    Returns:
        Dictionary with deletion results and statistics including:
        - success: Boolean indicating if operation was successful
        - message: Human-readable message about the operation
        - deleted_count: Number of designs that were deleted
        - user_id: The user ID that was cleared (if specified)
        - sessions_updated: Number of sessions that had their counts updated
    """
    try:
        storage = get_mongodb_storage()
        result = storage.clear_all_cell_designs(user_id)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to clear cell designs: {str(e)}",
            "deleted_count": 0,
            "user_id": user_id
        }

# =========================================================================
# Battery Chemistry Prediction Tool
# =========================================================================

@mcp.tool()
def predict_chemistry_tool_info() -> str:
    """
    Description and usage for the predict_chemistry tool.

    Args:
        cell_nominal_voltage: Nominal voltage (V) - required.
        cell_gravimetric_density: Gravimetric energy density (Wh/kg) - required.
        cell_volumetric_density: Volumetric energy density (Wh/L) - optional, will be estimated if not provided.

    Returns:
        str: "Predicted Chemistry: ..." or error message.
        
    Note: The model requires both voltage and gravimetric density. Volumetric density will be estimated
    if not provided based on typical battery cell characteristics.
    """

@mcp.tool()
def predict_chemistry(
    cell_nominal_voltage: float = None, 
    cell_gravimetric_density: float = None,
    cell_volumetric_density: float = None
) -> str:
    """
    Predict the chemistry of a battery cell based on its characteristics.
    
    Args:
        cell_nominal_voltage: Nominal voltage (V) - required
        cell_gravimetric_density: Gravimetric energy density (Wh/kg) - required  
        cell_volumetric_density: Volumetric energy density (Wh/L) - optional, will be estimated if not provided
        
    Returns:
        str: Predicted chemistry or error message
        
    Note: The model requires both voltage and gravimetric density. Volumetric density will be estimated
    if not provided based on typical battery cell characteristics.
    """
    # Input validation
    if cell_nominal_voltage is None or cell_gravimetric_density is None:
        raise ValueError("Both cell_nominal_voltage and cell_gravimetric_density must be provided")
    
    if not (2.5 <= cell_nominal_voltage <= 4.0):
        raise ValueError("Cell nominal voltage must be between 2.5 and 4.0 V")
    
    if not (100 <= cell_gravimetric_density <= 4000):
        raise ValueError("Cell gravimetric energy density must be between 100 and 4000 Wh/kg")
    
    # Estimate volumetric density if not provided (typical range for Li-ion batteries)
    if cell_volumetric_density is None:
        # Estimate based on typical battery characteristics
        # Most Li-ion batteries have volumetric density roughly 2-3x gravimetric density
        cell_volumetric_density = cell_gravimetric_density * 2.5
        if cell_volumetric_density > 1000:  # Cap at reasonable maximum
            cell_volumetric_density = 1000
    
    if not (200 <= cell_volumetric_density <= 2000):
        raise ValueError("Cell volumetric energy density must be between 200 and 2000 Wh/L")

    try:
        # Load the trained model
        model_path = Path(__file__).parent / "battery_chemistry_model.joblib"
        model = joblib.load(model_path)
        
        # Prepare input data with all 3 required features
        input_data = np.array([[
            cell_nominal_voltage,
            cell_volumetric_density,
            cell_gravimetric_density
        ]])
        
        # Create DataFrame with correct column names
        input_df = pd.DataFrame(
            input_data,
            columns=["Nominal Voltage (V)", "Volumetric Energy Density (Wh/L)", "Gravimetric Energy Density (Wh/kg)"]
        )
        
        # Make prediction
        predicted_chemistry = model.predict(input_df)[0]
        
        # Get prediction probability
        probabilities = model.predict_proba(input_df)[0]
        max_probability = max(probabilities)
        
        # Get confidence level
        if max_probability > 0.8:
            confidence = "High"
        elif max_probability > 0.6:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return f"Predicted Chemistry: {predicted_chemistry} (Confidence: {confidence}, Probability: {max_probability:.2f})"
        
    except Exception as e:
        return f"Error predicting chemistry: {str(e)}"

# ======================================================================
# Cell Design Tools
# ======================================================================
@mcp.tool()
def get_valid_cell_design_aliases() -> dict:
    """
    Returns the list of valid parameter aliases for cell design.
    Use this to see which parameters you are allowed to set when calling get_cell_design. The aliases with
    dot notation can be used to specify nested attributes.
    """
    return {
        "description": "These are the only allowed parameter aliases for cell design. Use only these keys when calling get_cell_design.",
        "valid_aliases": VALID_CELL_DESIGN_ALIASES,
    }

@mcp.tool()
def get_cell_design_tool_info() -> str:
    """
    Provides description and instructions on how to use the get_cell_design tool.
    This and the get_valid_cell_design_aliases tool should be called every time the get_cell_design tool is used.
    Optimize the design within 1% tolerances of the target specifications.
    If the user provides cell dimensions, do not use the default values, but use the provided values instead.
    *Always* make sure that the smallest cell dimension is the thickness and the width, length or height are the largest dimensions.
    Always confirm the following parameters with the user *wait for confirmation before generating a cell design*:
    - Form factor (Prismatic, Cylindrical, Pouch)
    - Cell dimensions (thickness, width, height)
    - Electrode materials and configurations
    - Separator type and thickness
    - Electrolyte composition
    Use default values for all other parameters if not provided.
    Example:
    Pouch cell design parameters:
    {
    'Form factor': 'Pouch',
    'Positive electrode formulation': 'LFP',
    'Negative electrode formulation': 'Graphite',
    'Cell height [mm]': 200,
    'Cell width [mm]': 150,
    'Cell volume packing ratio': 0.9,
    'Positive electrode sheet count': 20
    }
    Cylindrical cell design parameters:
    {
    'Form factor': 'Cylindrical',
    'Cell height [mm]': 95,
    'Cell diameter [mm]': 46,
    'Cell volume packing ratio': 0.9,
    'Negative electrode formulation': 'Graphite',
    'Positive electrode formulation': 'NMC811',
    'Negative electrode coating thickness [um]': 65,
    'Negative electrode mass loading [mg.cm-2]': 11,
    'Positive electrode coating thickness [um]': 60,
    'Positive electrode mass loading [mg.cm-2]': 18
    }
    """
    return (
        "Before I can help you further, I would need the confirmation of the following parameters:\n\n"
        "- Form factor (Prismatic, Cylindrical, Pouch)\n"
        "- Cell dimensions (thickness, width, height)\n"
        "- Electrode materials and configurations\n"
        "- Separator type and thickness\n"
        "- Electrolyte composition\n\n"
        "Please provide some or all of these parameters to proceed with the cell design generation. "
        "I will use default values for any parameters you don't specify."
    )

@mcp.tool()
@with_timeout(TOOL_TIMEOUT)
def get_cell_design(
    cell_design_parameters: dict,
    target_specifications: dict,
    force_store: bool = False,
    user_id: Optional[str] = None,
    session_id: str = None,
) -> dict:
    """
    Always call get_cell_design_tool_info and get_valid_cell_design_aliases before calling this tool.
    Create and stores a cell design based on the specified cell design parameters and target specifications.
    Keep on optimizing the design within 1% tolerances of the target specifications.
    Args:
        cell_design_parameters: Dictionary of key cell design parameters to create the design
        target_specifications: Dictionary of target specifications to optimize against
        force_store: If True, the design will be stored even if it already exists in the database
    Returns:
        A dictionary containing the status of cell design optimization, id of the design stored in the database, and any error messages.
        e.g. {"cell_design":{
                "id": "unique_design_id",
                "description": description,
                "context": context,
                "keywords": keywords,
                "stored_at": datetime.now().isoformat(),
                "cell_design_parameters": {
                    "Form factor": cell_design_parameters.get("Form factor"),
                    "Cell height [mm]": cell_design_parameters.get("Cell height [mm]"),
                    "Cell diameter [mm]": cell_design_parameters.get("Cell diameter [mm]"),
                    "Cell volume packing ratio": cell_design_parameters.get("Cell volume packing ratio"),
                    "Negative electrode formulation": cell_design_parameters.get("Negative electrode formulation"),
                    "Positive electrode formulation": cell_design_parameters.get("Positive electrode formulation"),
                    "Negative electrode coating thickness [um]": cell_design_parameters.get("Negative electrode coating thickness [um]"),
                    "Negative electrode mass loading [mg.cm-2]": cell_design_parameters.get("Negative electrode mass loading [mg.cm-2]"),
                    "Positive electrode coating thickness [um]": cell_design_parameters.get("Positive electrode coating thickness [um]"),
                    "Positive electrode mass loading [mg.cm-2]": cell_design_parameters.get("Positive electrode mass loading [mg.cm-2]"),
                    ...
                },
                "bill_of_materials": {...},
            }, "isError": False}
    """
    # Use the global list of valid aliases
    valid_aliases = set(VALID_CELL_DESIGN_ALIASES)
    print(f"user_id: {user_id}")
    # Check for invalid keys if not an internal call
    for key in cell_design_parameters:
        if key not in valid_aliases:
            raise ValueError(
                f"Unrecognized parameter '{key}'. "
                "Check for typos or use the correct field alias as defined in the model."
            )

    if "Form factor" not in cell_design_parameters:
        raise ValueError(
            "Form factor:Prismatic, Pouch, or Cylindrical must be specified in cell design parameters."
        )

    if cell_design_parameters["Form factor"].lower() not in [
        "prismatic",
        "cylindrical",
        "pouch",
    ]:
        raise ValueError(
            "Form factor must be either 'Prismatic', 'Cylindrical', or 'Pouch'."
        )

    # If positive and negative electrode formulation is not provided, raise an error
    if "Positive electrode formulation" not in cell_design_parameters:
        raise ValueError(
            "Positive electrode formulation must be specified in the format: Positive electrode formulation: 'LFP', 'NMC811', etc."
        )
    if "Negative electrode formulation" not in cell_design_parameters:
        raise ValueError(
            "Negative electrode formulation must be specified in the format: Negative electrode formulation: 'Graphite', 'Si', etc."
        )

    # Convert string electrode formulations to ElectrodeFormulation objects
    # This ensures mass fraction distribution is applied correctly
    for key in ["Positive electrode formulation", "Negative electrode formulation"]:
        if key in cell_design_parameters:
            formulation_data = cell_design_parameters[key]
            if isinstance(formulation_data, str):
                # Create ElectrodeFormulation from string name
                try:
                    ef = ElectrodeFormulation(formulation_data)
                    cell_design_parameters[key] = ef.as_alias_dict()
                except ValueError as e:
                    raise ValueError(
                        f"Invalid formulation '{formulation_data}' for {key}. "
                        f"Error: {str(e)}"
                    )
            elif isinstance(formulation_data, dict):
                # Create ElectrodeFormulation from dict, which will apply mass fraction distribution
                try:
                    ef = ElectrodeFormulation(formulation_data)
                    cell_design_parameters[key] = ef.as_alias_dict()
                except Exception as e:
                    raise ValueError(
                        f"Invalid formulation data for {key}. "
                        f"Error: {str(e)}"
                    )

    # Handle dot notation for nested attributes
    nested_keys = [k for k in cell_design_parameters if "." in k]
    for k in nested_keys:
        parts = k.split(".")
        base = parts[0]
        # If base has [ in it, it is not a valid base
        if "[" in base:
            continue
        subkey = ".".join(parts[1:])
        if base not in cell_design_parameters or not isinstance(
            cell_design_parameters[base], dict
        ):
            cell_design_parameters[base] = {}
        cell_design_parameters[base][subkey] = cell_design_parameters[k]
        del cell_design_parameters[k]

    cell_design = CellDesign.from_overrides(cell_design_parameters)

    # Ensure all fields including computed fields are included
    result = cell_design.model_dump(by_alias=True, mode="python")

    # Update the upper and lower voltage cut-offs for LFP cells
    if (
        "Positive electrode formulation" in result
        and result["Positive electrode formulation"]["Primary active material"] == "LFP"
    ):
        result["Upper voltage cut-off [V]"] = 3.65
        result["Lower voltage cut-off [V]"] = 2.5

    # Create keywords, context, and description
    keywords = extract_keywords_from_parameters(result)
    context = generate_context_description("get_cell_design", result)
    description = f"Cell design with {result.get('Form factor', 'unknown')} form factor"

    # Add power/thermal context if relevant parameters are present
    if any(
        key in cell_design_parameters
        for key in ["Cell thermal resistance [K.W-1]", "Cell cooling arc [degree]"]
    ):
        context += " - thermal analysis"

    if "Positive electrode formulation" in result:
        pos_form = result["Positive electrode formulation"]
        description += f", {pos_form.get('Primary active material', 'unknown')} cathode"
    if "Negative electrode formulation" in result:
        neg_form = result["Negative electrode formulation"]
        description += f", {neg_form.get('Primary active material', 'unknown')} anode"
    if "Cell nominal capacity [A.h]" in result:
        description += f", {result['Cell nominal capacity [A.h]']:.1f}Ah capacity"

    # Validate design before storing
    for key in target_specifications:
        if "capacity" in key.lower():
            # Check if the design meets the capacity target
            if not (
                target_specifications[key] * 0.99
                < result["Cell nominal capacity [A.h]"]
                < target_specifications[key] * 1.01
            ):
                current_pos_ml = result['Positive electrode mass loading [mg.cm-2]']
                current_mass_fraction = result['Positive electrode formulation']['Primary active material mass fraction']
                current_volume_packing_ratio = result['Cell volume packing ratio']
                pos_ml = target_specifications[key]/result['Cell nominal capacity [A.h]']*result['Positive electrode mass loading [mg.cm-2]']
                if pos_ml <= POSITIVE_ELECTRODE_MASS_LOADING_MIN:
                    pos_active_material_mass_fraction = pos_ml * current_mass_fraction/POSITIVE_ELECTRODE_MASS_LOADING_MIN
                    pos_ml = POSITIVE_ELECTRODE_MASS_LOADING_MIN
                    MSG_CYL= f"Consider changing the positive electrode mass loading, which is {current_pos_ml} to {pos_ml} and positive electrode active material mass fraction, which is {current_mass_fraction} below {pos_active_material_mass_fraction} to meet the target. "
                elif pos_ml > POSITIVE_ELECTRODE_MASS_LOADING_MAX:
                    pos_active_material_mass_fraction = pos_ml * current_mass_fraction/POSITIVE_ELECTRODE_MASS_LOADING_MAX
                    pos_ml = POSITIVE_ELECTRODE_MASS_LOADING_MAX
                    if pos_active_material_mass_fraction > 0.98:
                        MSG_CYL= f"Consider changing the positive electrode mass loading, which is {current_pos_ml} to {pos_ml}, positive electrode active material mass fraction, which is {current_mass_fraction} to 0.98 and cell volume packing ratio above {current_volume_packing_ratio} to meet the target. "

                    else:
                        MSG_CYL= f"Consider changing the positive electrode mass loading, which is  to {pos_ml} and positive electrode active material mass fraction, which is {current_mass_fraction} above {pos_active_material_mass_fraction} to meet the target. "
                else:
                    MSG_PRISM_POUCH = f"Consider changing the positive electrode mass loading, which is {current_pos_ml}, to {pos_ml} to meet the target."
                    MSG_CYL = f"Consider changing the positive electrode mass loading, which is {current_pos_ml}, to {pos_ml} to meet the target."
                if result["Positive electrode sheet count"] != int(target_specifications[key]/result['Cell nominal capacity [A.h]']*result['Positive electrode sheet count']):
                    MSG_PRISM_POUCH = f"Consider adjusting the positive electrode sheet count, which is {result['Positive electrode sheet count']}, to {int(target_specifications[key]/result['Cell nominal capacity [A.h]']*result['Positive electrode sheet count'])} to meet the target."
                else:
                    MSG_PRISM_POUCH = f"Consider changing the positive electrode mass loading, which is {result['Positive electrode mass loading [mg.cm-2]']}, to {target_specifications[key]/result['Cell nominal capacity [A.h]']*result['Positive electrode mass loading [mg.cm-2]']} to meet the target."

                MSG_OUT = (
                    MSG_PRISM_POUCH
                    if result["Form factor"].lower() in ["prismatic", "pouch"]
                    else MSG_CYL
                )
                raise ValueError(
                    f"Design {key} is {round(result['Cell nominal capacity [A.h]'],1)}Ah, which is not within 1% tolerance of the target capacity of {target_specifications[key]}Ah. {MSG_OUT}"
                )

    # Create a sorted string representation for consistent hashing
    cell_design_str = json.dumps(result, sort_keys=True, default=str)
    id = hashlib.md5(cell_design_str.encode()).hexdigest()[:8]
    # Get bill of materials
    bom = estimate_bill_of_materials(
        user_id=user_id,
        cell_design_parameters=result
    )["bill_of_materials"]
    result = {
        "design_hash": id,
        "description": description,
        "context": context,
        "keywords": keywords,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cell_design_parameters": result,
        "bill_of_materials": bom,
    }
    if not force_store:
        search_results = search_cell_designs_in_db(
            user_id=user_id,
            keywords=keywords,
            context=context,
            limit=10,
        )
        if search_results.get("total_found", 0) > 0:
            output = {
                "status": "success",
                "cell_design_id": search_results["results"][0],
                "message": f"Similar design already exists with ID {search_results['results'][0]}.",
            }
            return output
    output = store_cell_design_in_db(
        cell_design=result,
        user_id=user_id,
        session_id=session_id,
    )
    if output.get("status") == "success":
        # cell_design_id is already set by store_cell_design_in_db
        output["message"] = f"New design stored with ID {output['cell_design_id']}."
    else:
        raise Exception(f"Failed to store design: {output.get('message', 'unknown error')}")
    return output

@mcp.tool()
def estimate_bill_of_materials(
    user_id: Optional[str] = None, 
    cell_design_id: str = None,
    cell_design_parameters: dict = None
) -> dict:
    """
    Estimate bill of materials for a battery cell design including component weights down to active material powders.
    *Always* check if the cell design exists in the database by calling fetch_cell_design_from_db.
    If it does not, use the cell_design_parameters to create a new cell design.
        Args:
            user_id: Automatically set by the MCP server
            cell_design_id: Cell design ID (optional)
            cell_design_parameters: Dictionary of cell design parameters (optional)

        Returns:
            Dictionary with bill of materials breakdown
    """
    # Handle previous design lookup
    if cell_design_parameters is None:
        db_result = fetch_cell_design_from_db(
            user_id=user_id, 
            cell_design_id=cell_design_id
        )
        if db_result.get("status", "failed") != "success":
            raise Exception(db_result.get("message", "Failed to fetch cell design"))
        active_cell_design = db_result["cell_design"]["cell_design_parameters"]
    else:
        active_cell_design = CellDesign.from_overrides(cell_design_parameters)

    # Ensure active_cell_design is a dictionary for consistent access
    if hasattr(active_cell_design, "model_dump"):
        active_cell_design = active_cell_design.model_dump(by_alias=True, mode="python")
    elif not isinstance(active_cell_design, dict):
        active_cell_design = dict(active_cell_design)

    # Calculate bill of materials
    bom = {}
    
    # We'll calculate total mass at the end after calculating all components

    # Get electrode formulations
    pos_form = active_cell_design["Positive electrode formulation"]
    neg_form = active_cell_design["Negative electrode formulation"]

    # Calculate electrode coating masses
    pos_coating_mass = (
        active_cell_design["Positive electrode sheet count"]
        * active_cell_design["Positive electrode sheet height [mm]"]
        * active_cell_design["Positive electrode sheet width [mm]"]
        * active_cell_design["Positive electrode mass loading [mg.cm-2]"]
        * 2
        * 1e-5  # 2 sides, convert units
    )

    neg_coating_mass = (
        active_cell_design["Negative electrode sheet count"]
        * active_cell_design["Negative electrode sheet height [mm]"]
        * active_cell_design["Negative electrode sheet width [mm]"]
        * active_cell_design["Negative electrode mass loading [mg.cm-2]"]
        * 2
        * 1e-5  # 2 sides, convert units
    )

    # Add electrode materials
    # Convert pos_form and neg_form to dicts if they are not already
    if not isinstance(pos_form, dict):
        # If pos_form is a Pydantic model or similar, use model_dump
        if hasattr(pos_form, "model_dump"):
            pos_form = pos_form.model_dump(by_alias=True, mode="python")
        else:
            pos_form = dict(pos_form)
    if not isinstance(neg_form, dict):
        if hasattr(neg_form, "model_dump"):
            neg_form = neg_form.model_dump(by_alias=True, mode="python")
        else:
            neg_form = dict(neg_form)

    pos_materials = [
        (
            pos_form.get("Primary active material"),
            pos_form.get("Primary active material mass fraction"),
        ),
        (
            pos_form.get("Secondary active material"),
            pos_form.get("Secondary active material mass fraction"),
        ),
        (pos_form.get("Primary binder"), pos_form.get("Primary binder mass fraction")),
        (
            pos_form.get("Secondary binder"),
            pos_form.get("Secondary binder mass fraction"),
        ),
        (
            pos_form.get("Primary conductive agent"),
            pos_form.get("Primary conductive agent mass fraction"),
        ),
    ]

    for material, fraction in pos_materials:
        if material and fraction and fraction > 0:
            weight = pos_coating_mass * fraction
            bom[material] = bom.get(material, 0) + weight

    neg_materials = [
        (
            neg_form.get("Primary active material"),
            neg_form.get("Primary active material mass fraction"),
        ),
        (
            neg_form.get("Secondary active material"),
            neg_form.get("Secondary active material mass fraction"),
        ),
        (neg_form.get("Primary binder"), neg_form.get("Primary binder mass fraction")),
        (
            neg_form.get("Secondary binder"),
            neg_form.get("Secondary binder mass fraction"),
        ),
    ]

    for material, fraction in neg_materials:
        if material and fraction and fraction > 0:
            weight = neg_coating_mass * fraction
            bom[material] = bom.get(material, 0) + weight

    # Add current collectors
    pos_foil_mass = (
        active_cell_design["Positive electrode sheet count"]
        * active_cell_design["Positive electrode sheet height [mm]"]
        * active_cell_design["Positive electrode sheet width [mm]"]
        * active_cell_design["Positive electrode foil thickness [um]"]
        * active_cell_design["Positive electrode foil density [g.cm-3]"]
        * 1e-7
    )
    bom["Aluminum"] = pos_foil_mass

    neg_foil_mass = (
        active_cell_design["Negative electrode sheet count"]
        * active_cell_design["Negative electrode sheet height [mm]"]
        * active_cell_design["Negative electrode sheet width [mm]"]
        * active_cell_design["Negative electrode foil thickness [um]"]
        * active_cell_design["Negative electrode foil density [g.cm-3]"]
        * 1e-7
    )
    bom["Copper"] = neg_foil_mass

    # Add other components
    sep_mass = (
        active_cell_design["Separator sheet count"]
        * active_cell_design["Separator sheet height [mm]"]
        * active_cell_design["Separator sheet width [mm]"]
        * active_cell_design["Separator areal density [g.m-2]"]
        * 1e-6
    )
    separator_composition = active_cell_design.get("Separator composition", "PE/PP")
    bom[f"Separator ({separator_composition})"] = sep_mass

    # Calculate electrolyte mass if not present
    if "Electrolyte mass [g]" not in active_cell_design:
        # Estimate based on cell capacity (typically 2g per Ah)
        cell_capacity = active_cell_design.get("Cell nominal capacity [A.h]", 0.0)
        electrolyte_mass = cell_capacity * 2.0  # 2g per Ah
    else:
        electrolyte_mass = active_cell_design["Electrolyte mass [g]"]
    bom["Electrolyte"] = electrolyte_mass
    # Calculate cell casing mass if not present
    casing_material = active_cell_design.get("Cell casing material", {})
    if isinstance(casing_material, dict):
        casing_name = casing_material.get("Name", "Aluminum")
        casing_density = casing_material.get("Density [g.cm-3]", 2.7)  # Default aluminum density
    else:
        casing_name = "Aluminum"
        casing_density = 2.7
    
    if "Cell casing mass [g]" not in active_cell_design:
        # Calculate casing mass based on dimensions and density
        cell_height = active_cell_design.get("Cell height [mm]", 0.0) * 0.1  # mm to cm
        cell_width = active_cell_design.get("Cell width [mm]", 0.0) * 0.1
        cell_thickness = active_cell_design.get("Cell thickness [mm]", 0.0) * 0.1
        casing_thickness = active_cell_design.get("Cell casing thickness [mm]", 0.5) * 0.1
        
        # Calculate casing volume (simplified as outer volume minus inner volume)
        outer_volume = cell_height * cell_width * cell_thickness
        inner_height = cell_height - 2 * casing_thickness
        inner_width = cell_width - 2 * casing_thickness
        inner_thickness = cell_thickness - 2 * casing_thickness
        inner_volume = max(0, inner_height * inner_width * inner_thickness)
        casing_volume = outer_volume - inner_volume
        casing_mass = casing_volume * casing_density
    else:
        casing_mass = active_cell_design["Cell casing mass [g]"]
    
    bom[casing_name] = casing_mass

    # Calculate total mass from all components
    if active_cell_design["Cell mass [g]"] is not None:
        total_mass = active_cell_design["Cell mass [g]"]
    else:
        total_mass = sum(bom.values())

    # Create summary with percentages
    bom_with_percentages = {}

    for material, weight in sorted(bom.items(), key=lambda x: x[1], reverse=True):
        percentage = (weight / total_mass * 100) if total_mass > 0 else 0
        bom_with_percentages[material] = {
            "weight_g": round(weight, 2),
            "percentage": round(percentage, 1),
        }

    return {
        "total_cell_weight_g": round(total_mass, 2),
        "cell_capacity_Ah": round(active_cell_design["Cell nominal capacity [A.h]"], 2),
        "cell_energy_Wh": round(active_cell_design["Cell nominal energy [W.h]"], 2),
        "bill_of_materials": bom_with_percentages,
    }

# =======================================================================================
# Physics based simulations
# =======================================================================================
# ===============================================================================
# Helper Functions
# ===============================================================================

@mcp.tool()
def setup_cell_models_tool_info() -> str:
    """
    Provides description and instructions on how to use the setup_cell_models tool.
    This tool should be called every time the setup_cell_models tool is used.
    """
    return (
        "This function sets up physics-based simulation models (SPM and SPMeT) based on cell design parameters.\n"
        "- Must be run before any performance simulations (get_cell_power, check_cell_performance)\n"
        "- *Always* specify the model type as either 'SPMeT', or 'SPM'. *First* run the tool with model_type='SPM'.\n"
        "- *Always* run the tool with model_type='SPM', and then run the tool with model_type='SPMeT'.\n"
        "Required Args:\n"
        "    cell_design_id (str): Unique identifier for the cell design stored in the database\n"
        "    model_type (str): Model type to setup. Default is 'SPMeT'. Other options are 'SPM'.\n"
        "\n"
        "Optional Args:\n"
        "    user_id (str): Automatically set by the MCP server\n"
        "Prerequisites:\n"
        "    - Cell design must already exist in the database (created via get_cell_design)\n"
        "    - Cell design must have valid cell_design_parameters\n"
        "\n"
        "Returns:\n"
        "    dict: Setup status and model information\n"
        '        - status (str): "success", "complete", or "failed"\n'
        "        - models (list/dict): Available model types or model configurations\n"
        "        - message (str): Status message or error details\n"
        "        - isError (bool): Error flag for compatibility\n"
        "\n"
        "Error Handling:\n"
        "    - Database access validation\n"
        "    - Cell design existence verification\n"
        "    - Parameter completeness checks\n"
        "    - Model creation error handling\n"
        "\n"
        "Status Responses:\n"
        '    - "success": Models created successfully\n'
        '    - "complete": Models already exist (no action needed)\n'
        '    - "failed": Error occurred during setup\n'
        "\n"
        "Usage Notes:\n"
        "    - Only needs to be run once per cell design\n"
        "    - Automatically detects if models already exist\n"
        "    - Required before running any simulation tools\n"
        "\n" + TOOL_INFO_FOOTER
    )

@mcp.tool()
@with_timeout(TOOL_TIMEOUT)
def setup_cell_models(cell_design_id: str, user_id: Optional[str], model_type: str = "SPMeT") -> dict:
    """
    Setup physics models based on the cell design parameters.
    This function initializes the SPM and SPMeT models with the appropriate parameters.
    Args:
        user_id (str): Automatically set by the MCP server.
        cell_design_id (str): Cell design stored in the session.
        model_type (str): Model type to setup. Default is "SPMeT". Other options are "SPM".
    Example:
        >>> setup_cell_models(
                cell_design_id="unique_design_id"
                model_type="SPM"
            )
        Output:
        {"status": "success", "models": {"SPM": {...}, "SPMeT": {...}}, "isError": False}
    """
    # Add the PyBaMM model parameters
    # Step 1a: Default parameters for O'Regan2022 (More thermal dependency)
    default_parameter_set = "ORegan2022"
    db_result = fetch_cell_design_from_db(
        user_id=user_id, cell_design_id=cell_design_id
    )
    if db_result.get("status", "failed") != "success":
        # If the db_result is not successful, return an error message
        return {"status": "failed", "models": {}, "message": "Cell design not found or database error."}
    # Only proceed if status is success
    # Check if optimized_parameters already exist for the model_type
    if (
        "cell_simulation_models" in db_result["cell_design"]
        and model_type in db_result["cell_design"]["cell_simulation_models"]
        and "optimized_parameters" in db_result["cell_design"]["cell_simulation_models"][model_type]
    ):
        return {
            "status": "complete",
            "models": {model_type: db_result["cell_design"]["cell_simulation_models"][model_type]},
            "message": "Cell models already exist in the design."
        }
    cell_design = db_result["cell_design"]
    cell_design_parameters = cell_design["cell_design_parameters"]

    logging.info(cell_design_parameters)
    # Update the upper and lower voltage cut-offs for LFP cells
    if (
        "Positive electrode formulation" in cell_design
        and cell_design["Positive electrode formulation"]["Primary active material"]
        == "LFP"
    ):
        default_parameter_set = "Prada2013"

    model_SPM = {
        "SPM": {
            "model_description": "Single Particle Model",
            "model_options": {
                "calculate discharge energy": "true",
            },
            "default_parameter_set": default_parameter_set,
        }
    }
    # DFN model is no longer supported
    # model_DFN = {
    #     "DFN": {
    #         "model_description": "Isothermal Doyle-Fuller-Newman (P2D) model",
    #         "model_options": {
    #             "calculate discharge energy": "true",
    #         },
    #         "default_parameter_set": default_parameter_set,
    #     }
    # }
    model_SPMeT = {
        "SPMeT": {
            "model_description": "Lumped Thermal model coupled with Single Particle Model with electrolyte effects",
            "model_options": {
                "calculate discharge energy": "true",
                "cell geometry": "arbitrary",
                "thermal": "lumped",
                "contact resistance": "true",
            },
            "default_parameter_set": default_parameter_set,
        }
    }
    if model_type == "SPM":
        updated_model_SPM = update_model_parameters(
            cell_design_parameters=cell_design_parameters,
            cell_model=model_SPM,
        )["models"]["SPM"]
        results = update_cell_design_in_db(
            user_id=user_id,
            cell_design_id=cell_design_id,
            updates={
                "cell_simulation_models": {
                    "SPM": updated_model_SPM,
                }
            },
        )
    elif model_type == "SPMeT":
        optimized_parameters = None
        if (
            cell_design is not None
            and isinstance(cell_design, dict)
            and "cell_simulation_models" in cell_design
            and isinstance(cell_design["cell_simulation_models"], dict)
            and "SPM" in cell_design["cell_simulation_models"]
            and isinstance(cell_design["cell_simulation_models"]["SPM"], dict)
            and "optimized_parameters" in cell_design["cell_simulation_models"]["SPM"]
        ):
            optimized_parameters = cell_design["cell_simulation_models"]["SPM"]["optimized_parameters"]
        else:
            return {
                "status": "failed",
                "models": {},
                "message": "SPM model or its optimized_parameters not found in cell_design. Run 'setup_cell_models' with model_type='SPM' to set up the SPM model.",
            }
        model_SPMeT['SPMeT']["optimized_parameters"] = optimized_parameters
        updated_model_SPMeT = update_model_parameters(
            cell_design_parameters=cell_design_parameters,
            cell_model=model_SPMeT,
        )["models"]["SPMeT"]
        results = update_cell_design_in_db(
            user_id=user_id,
            cell_design_id=cell_design_id,
            updates={
                "cell_simulation_models": {
                    "SPMeT": updated_model_SPMeT,
                }
            },
        )
    elif model_type == "DFN":
    #     # Validate nested keys before accessing
    #     optimized_parameters = None
    #     if (
    #         cell_design is not None
    #         and isinstance(cell_design, dict)
    #         and "cell_simulation_models" in cell_design
    #         and isinstance(cell_design["cell_simulation_models"], dict)
    #         and "SPMeT" in cell_design["cell_simulation_models"]
    #         and isinstance(cell_design["cell_simulation_models"]["SPMeT"], dict)
    #         and "optimized_parameters" in cell_design["cell_simulation_models"]["SPMeT"]
    #     ):
    #         optimized_parameters = cell_design["cell_simulation_models"]["SPMeT"]["optimized_parameters"]
    #     else:
    #         return {
    #             "status": "failed",
    #             "models": {},
    #             "message": "SPMeT model or its optimized_parameters not found in cell_design.",
    #         }
    #     model_DFN['DFN']["optimized_parameters"] = optimized_parameters
    #     updated_model_DFN = update_model_parameters(
    #         cell_design_parameters=cell_design_parameters,
    #         cell_model=model_DFN,
    #     )["models"]["DFN"]
    #     results = update_cell_design_in_db(
    #         user_id=user_id,
    #         cell_design_id=cell_design_id,
    #         updates={
    #             "cell_simulation_models": {
    #                 "DFN": updated_model_DFN,
    #             }
    #         },
    #     )
    # else:
        return {"status": "failed", "models": {}, "message": "Invalid model type. Valid model types are 'SPM' and 'SPMeT'."}
    return results

def update_model_parameters(
    cell_design_parameters: dict,
    cell_model: dict,
) -> dict:
    """
    Update model parameters based on cell design parameters.

    Args:
        cell_design_parameters (dict): Cell design parameters to apply.
        cell_models (dict): Existing parameter values to update.

    Returns:
        output_model_parameters (dict): Updated parameter values.

    Example:
        >>> update_model_parameters(
                cell_design_parameters={
                    "Cell cooling surface area [mm2]": 100,
                    ...
                },
                cell_model={
                    "SPMeT": {
                        "model_description": "Isothermal Doyle-Fuller-Newman (P2D) model",
                        "model_options": {
                            "calculate discharge energy": "true",
                            ...
                        },
                        "model_default_parameter_set": "ORegan2022",
                    }
                })

        Output: {
                    "cell_model": {
                        "SPMeT": {
                            "model_description": "Isothermal Doyle-Fuller-Newman (P2D) model",
                            "model_options": {
                                "calculate discharge energy": "true",
                                ...
                            },
                            "model_default_parameter_set": "ORegan2022",
                            "updated_parameters": {...}
                        }
                    },
                    "isError": False
                }
    Raises:
        ValueError: If cell_model is None.
    """

    if cell_model is None:
        raise ValueError(
            "Parameter values must be provided to update model parameters."
        )

    # Pybamm to CellDesign mapping
    pybamm_to_cell_design = {
        # 'Ambient temperature [K]': 298.15,
        # 'Boltzmann constant [J.K-1]': 1.380649e-23,
        # 'Cation transference number': <function electrolyte_transference_number_EC_EMC_3_7_Landesfeind2019 at 0x137f314e0>,
        # "Cell cooling surface area [m2]": cell_design_parameters[
        #     "Cell cooling surface area [mm2]"
        # ]
        # * 1e-6,
        "Cell volume [m3]": round(cell_design_parameters["Cell volume [L]"], 3) * 1e-3,
        # 'Contact resistance [Ohm]': 0,
        # 'Current function [A]': 5.0,
        "Electrode height [m]": round(
            cell_design_parameters["Positive electrode sheet height [mm]"], 3
        )
        * 1e-3,
        "Electrode length [m]": round(
            cell_design_parameters["Positive electrode sheet width [mm]"], 3
        )
        * 1e-3,
        "Electrode width [m]": round(
            cell_design_parameters["Positive electrode sheet width [mm]"], 3
        )
        * 1e-3,
        # 'Electrolyte conductivity [S.m-1]': <function electrolyte_conductivity_EC_EMC_3_7_Landesfeind2019 at 0x137f316c0>,
        # 'Electrolyte diffusivity [m2.s-1]': <function electrolyte_diffusivity_EC_EMC_3_7_Landesfeind2019 at 0x137f31620>,
        # 'Electron charge [C]': 1.602176634e-19,
        # 'Faraday constant [C.mol-1]': 96485.33212331001,
        # 'Ideal gas constant [J.K-1.mol-1]': 8.31446261815324,
        # 'Initial concentration in electrolyte [mol.m-3]': 1000.0,
        # 'Initial concentration in negative electrode [mol.m-3]': 28866.0,
        # 'Initial concentration in positive electrode [mol.m-3]': 13975.0,
        # 'Initial temperature [K]': 298.15,
        "Lower voltage cut-off [V]": cell_design_parameters[
            "Lower voltage cut-off [V]"
        ],
        # 'Maximum concentration in negative electrode [mol.m-3]': 29583.0,
        # 'Maximum concentration in positive electrode [mol.m-3]': 51765.0,
        "Negative current collector conductivity [S.m-1]": 58411000.0,
        "Negative current collector density [kg.m-3]": 8933.0,
        "Negative current collector specific heat capacity [J.kg-1.K-1]": 385.0,
        "Negative current collector thermal conductivity [W.m-1.K-1]": 400.0,
        "Negative current collector thickness [m]": round(
            cell_design_parameters["Negative electrode foil thickness [um]"], 3
        )
        * 1e-6,
        # 'Negative electrode Bruggeman coefficient (electrode)': 0.0,
        # 'Negative electrode Bruggeman coefficient (electrolyte)': 1.5,
        # 'Negative electrode OCP [V]': <function graphite_LGM50_ocp_Chen2020 at 0x137f30cc0>,
        # 'Negative electrode OCP entropic change [V.K-1]': <function graphite_LGM50_entropic_change_ORegan2022 at 0x137f30f40>,
        "Negative electrode active material volume fraction": round(
            cell_design_parameters[
                "Negative electrode active material volume fraction"
            ],
            3,
        ),
        # 'Negative electrode charge transfer coefficient': 0.5,
        # 'Negative electrode conductivity [S.m-1]': 215.0,
        "Negative electrode density [kg.m-3]": round(
            cell_design_parameters["Negative electrode coating density [g.cm-3]"], 3
        )
        * 1e3,
        # 'Negative electrode double-layer capacity [F.m-2]': 0.2,
        # 'Negative electrode exchange-current density [A.m-2]': <function graphite_LGM50_electrolyte_exchange_current_density_ORegan2022 at 0x137f30d60>,
        "Negative electrode porosity": cell_design_parameters[
            "Negative electrode porosity"
        ],
        "Negative electrode specific heat capacity [J.kg-1.K-1]": 710.0,
        # 'Negative electrode thermal conductivity [W.m-1.K-1]': <function graphite_LGM50_thermal_conductivity_ORegan2022 at 0x137f30ea0>,
        "Negative electrode thickness [m]": round(
            cell_design_parameters["Negative electrode coating thickness [um]"], 0
        )
        * 1e-6,
        # 'Negative particle diffusivity [m2.s-1]': <function graphite_LGM50_diffusivity_ORegan2022 at 0x137f30c20>,
        # 'Negative particle radius [m]': 5.86e-06,
        # "Nominal cell capacity [A.h]": cell_design_parameters[
        #     "Cell nominal capacity [A.h]"
        # ],
        # 'Number of cells connected in series to make a battery': 1.0,
        # 'Number of electrodes connected in parallel to make a cell': 1.0,
        # 'Open-circuit voltage at 0% SOC [V]': 2.5,
        # 'Open-circuit voltage at 100% SOC [V]': 4.4,
        "Positive current collector conductivity [S.m-1]": 36914000.0,
        "Positive current collector density [kg.m-3]": 2702.0,
        "Positive current collector specific heat capacity [J.kg-1.K-1]": 897.0,
        "Positive current collector thermal conductivity [W.m-1.K-1]": 237.0,
        "Positive current collector thickness [m]": round(
            cell_design_parameters["Positive electrode foil thickness [um]"], 3
        )
        * 1e-6,
        # 'Positive electrode Bruggeman coefficient (electrode)': 0.0,
        # 'Positive electrode Bruggeman coefficient (electrolyte)': 1.5,
        # 'Positive electrode OCP [V]': <function nmc_LGM50_ocp_Chen2020 at 0x137f31120>,
        # 'Positive electrode OCP entropic change [V.K-1]': <function nmc_LGM50_entropic_change_ORegan2022 at 0x137f313a0>,
        "Positive electrode active material volume fraction": round(
            cell_design_parameters[
                "Positive electrode active material volume fraction"
            ],
            3,
        ),
        # 'Positive electrode charge transfer coefficient': 0.5,
        # 'Positive electrode conductivity [S.m-1]': <function nmc_LGM50_electronic_conductivity_ORegan2022 at 0x137f30fe0>,
        "Positive electrode density [kg.m-3]": round(
            cell_design_parameters["Positive electrode coating density [g.cm-3]"], 3
        )
        * 1e3,
        # 'Positive electrode double-layer capacity [F.m-2]': 0.2,
        # 'Positive electrode exchange-current density [A.m-2]': <function nmc_LGM50_electrolyte_exchange_current_density_ORegan2022 at 0x137f311c0>,
        "Positive electrode porosity": round(
            cell_design_parameters["Positive electrode porosity"], 3
        ),
        "Positive electrode specific heat capacity [J.kg-1.K-1]": 500.0,
        # 'Positive electrode thermal conductivity [W.m-1.K-1]': <function nmc_LGM50_thermal_conductivity_ORegan2022 at 0x137f31300>,
        "Positive electrode thickness [m]": round(
            cell_design_parameters["Positive electrode coating thickness [um]"], 0
        )
        * 1e-6,
        # 'Positive particle diffusivity [m2.s-1]': <function nmc_LGM50_diffusivity_ORegan2022 at 0x137f31080>,
        # 'Positive particle radius [m]': 5.22e-06,
        # 'Reference temperature [K]': 298.15,
        # 'Separator Bruggeman coefficient (electrode)': 1.5,
        # 'Separator Bruggeman coefficient (electrolyte)': 1.5,
        "Separator density [kg.m-3]": 1548.0,
        "Separator porosity": round(cell_design_parameters["Separator porosity"], 3),
        "Separator specific heat capacity [J.kg-1.K-1]": 2000.0,
        # 'Separator thermal conductivity [W.m-1.K-1]': 0.3344,
        "Separator thickness [m]": round(
            cell_design_parameters["Separator thickness [um]"], 0
        )
        * 1e-6,
        # 'Thermodynamic factor': <function electrolyte_TDF_EC_EMC_3_7_Landesfeind2019 at 0x137f31580>,
        # "Total heat transfer coefficient [W.m-2.K-1]": 10.0,
        "Upper voltage cut-off [V]": cell_design_parameters[
            "Upper voltage cut-off [V]"
        ],
        # Add missing parameter with default value
        "Exchange-current density for lithium metal electrode [A.m-2]": 1.0,
        # 'citations': ['ORegan2022',
        #               'Chen2020']
    }
    # Step 2c: Set model thermal parameters based
    thermal_paste_thickness_mm = 1  # Default thermal paste thickness in mm
    thermal_paste_conductivity_W_mK = 0.5  # Default thermal
    h_ext: float = (
        1
        / (
            thermal_paste_thickness_mm
            * 1e-3
            / (
                thermal_paste_conductivity_W_mK
                * cell_design_parameters["Cell cooling surface area [mm2]"]
                * 1e-6
            )
            + cell_design_parameters["Cell thermal resistance [K.W-1]"]
        )
        / cell_design_parameters["Cell cooling surface area [mm2]"]
        * 1e6
    )
    pybamm_to_cell_design.update(
        {
            "Total heat transfer coefficient [W.m-2.K-1]": round(h_ext, 3),
            "Cell cooling surface area [m2]": (
                round(cell_design_parameters["Cell cooling surface area [mm2]"], 3)
                * 1e-6
            ),
        },
        check_already_exists=False,
    )
    # Set the model
    base_parameter_values = None
    model = None
    model_type = None
    try:
        # if "DFN" in cell_model:
        #     model = pybamm.lithium_ion.DFN(
        #         options=cell_model["DFN"].get("model_options", {}),
        #     )
        #     model_type = "DFN"
        if "SPMeT" in cell_model:
            model = pybamm.lithium_ion.SPMe(
                options=cell_model["SPMeT"].get("model_options", {}),
            )
            model_type = "SPMeT"
        elif "SPM" in cell_model:
            model = pybamm.lithium_ion.SPM(
                options=cell_model["SPM"].get("model_options", {}),
            )
            model_type = "SPM"
        else:
            raise ValueError("Cell model must be either SPMeT, or SPM.")
            #

        base_parameter_values = pybamm.ParameterValues(
            cell_model[model_type]["default_parameter_set"]
        )
        # Update parameter values with cell design parameters
        output_parameter_values = base_parameter_values.copy()
        for key, value in pybamm_to_cell_design.items():
            # if key in output_parameter_values.keys():
            output_parameter_values.update({key: value}, check_already_exists=False)
        
        # Add any missing parameters that PyBaMM might need with default values
        missing_parameters = {
            "Exchange-current density for lithium metal electrode [A.m-2]": 1.0,
            "Lithium metal electrode exchange current density [A.m-2]": 1.0,
        }
        for key, value in missing_parameters.items():
            if key not in output_parameter_values:
                output_parameter_values.update({key: value}, check_already_exists=False)

        # Set the nominal cell capacity based on the cell design parameters
        scale_capacity: float = 0.5
        ocv100 = cell_design_parameters["Upper voltage cut-off [V]"]-0.1
        ocv0 = cell_design_parameters["Lower voltage cut-off [V]"]+0.1
        # Perform a discharge simulation to set the nominal cell capacity
        experiment = prep_simulation_experiment(
            {
                "name": "CAPACITY_MATCH",
                "voltage_max_V": cell_design_parameters["Upper voltage cut-off [V]"] if cell_design_parameters["Upper voltage cut-off [V]"]<=4.25 else 4.25,
                "cRate_ch": 0.1,
                "cRate_dis": 0.1,
                "voltage_min_V": cell_design_parameters["Lower voltage cut-off [V]"] if cell_design_parameters["Lower voltage cut-off [V]"]>=2.8 else 2.8,
            }
        )
        if 'optimized_parameters' in cell_model[model_type]:
            output_parameter_values.update(cell_model[model_type]["optimized_parameters"], check_already_exists=False)
        #clear the optimized parameters
        cell_model[model_type]["optimized_parameters"] = {}
        discharge_capacity = output_parameter_values["Nominal cell capacity [A.h]"]
        target_capacity = cell_design_parameters["Cell nominal capacity [A.h]"]
        scale_capacity = discharge_capacity / target_capacity
        iteration = 0
        for iteration in range(20):
            soln = None
            logging.info(f"Iteration {iteration}: Scale capacity: {scale_capacity}")
            sim = pybamm.Simulation(model, experiment=experiment, parameter_values=output_parameter_values)
            # solver = get_pybamm_solver(max_step_decrease_count=50, atol=1e-3, rtol=1e-3)
            solver = pybamm.IDAKLUSolver(atol=1e-3, rtol=1e-3, output_variables=["Time [s]", "Terminal voltage [V]", "Current [A]", "Discharge capacity [A.h]", "Discharge energy [W.h]", "Throughput capacity [A.h]", "Throughput energy [W.h]", "Volume-averaged cell temperature [K]", "Power [W]"])

            soln = sim.solve(initial_soc=0.8, solver=solver)
            MSG = ""
            if hasattr(soln, 'cycles'):
                logging.info(f"Number of cycles: {len(soln.cycles)}")
                for i, cycle in enumerate(soln.cycles):
                    MSG = MSG + f"Cycle {i}: {soln.cycles[i].termination}"
            
            # Check if solution has enough cycles and data
            if not hasattr(soln, 'cycles') or len(soln.cycles) < 4:
                raise ValueError(f"Solution has insufficient cycles. Expected at least 4, got {len(soln.cycles) if hasattr(soln, 'cycles') else 'None'}. {MSG}")
            
            # Verify required data exists in each cycle
            required_cycles = [1, 2, 3]  # Charge, Hold, Discharge cycles
            for cycle_idx in required_cycles:
                if cycle_idx >= len(soln.cycles):
                    raise ValueError(f"Cycle {cycle_idx} not found in solution. Available cycles: {list(range(len(soln.cycles)))}")
                
                if len(soln.cycles[cycle_idx]["Discharge capacity [A.h]"].entries) == 0:
                    raise ValueError(f"Discharge capacity data not found in cycle {cycle_idx}")
                
                if len(soln.cycles[cycle_idx]["Terminal voltage [V]"].entries) == 0:
                    raise ValueError(f"Voltage data not found in cycle {cycle_idx}")
            
            # Set the nominal cell capacity based on the discharge simulation
            # Convert PyBaMM values to regular Python numbers
            # Calculate the new scale capacity based on the simulation results
            if hasattr(soln, 'cycles') and len(soln.cycles) >= 3:
                discharge_capacity = float(
                soln.cycles[2]["Discharge capacity [A.h]"].entries[-1]
                - soln.cycles[2]["Discharge capacity [A.h]"].entries[0]
            )
                # Use a more stable scaling approach
                scale_capacity = discharge_capacity / target_capacity
                logging.info(f"Simulated capacity: {discharge_capacity}, Target: {target_capacity}, New scale: {scale_capacity}")
            else:
                logging.warning("Insufficient cycles for capacity calculation")
                break
            ocv100 = float(soln.cycles[1]["Terminal voltage [V]"].entries[-1])
            ocv0 = float(soln.cycles[3]["Terminal voltage [V]"].entries[-1])
            logging.info(f"Updated parameters with scale_capacity: {scale_capacity}")
            # Update the parameter values with the scaled capacity
            output_parameter_values.update(
                {
                    "Electrode width [m]": output_parameter_values["Electrode width [m]"] / scale_capacity,
                    "Nominal cell capacity [A.h]": discharge_capacity / scale_capacity,
                    "Open-circuit voltage at 100% SOC [V]": ocv100,
                    "Open-circuit voltage at 0% SOC [V]": ocv0,
                },
                check_already_exists=False,
            )
            if 0.9999 < scale_capacity < 1.0001:
                break
        
        # Check if we converged or hit max iterations
        logging.info(f"Scaling converged after {iteration} iterations. Final scale_capacity: {scale_capacity}")
        
        # Prepare the optimized parameters for the database
        # Update the parameter values with the scaled capacity
        # Get all the keys from the output_parameter_values that either have different values fron the base_parameter_values or are not in the base_parameter_values
        extracted_dict = {key: value for key, value in output_parameter_values.items() if key not in base_parameter_values or base_parameter_values[key] != value}
        cell_model[model_type]["optimized_parameters"] = extracted_dict
    except Exception as e:
        raise Exception(f"Error updating model parameters: {str(e)}")
    
    return {
        "status": "success",
        "models": cell_model,
        "message": "Successfully updated model parameters.",
    }

# @mcp.tool()
def prep_simulation_experiment(
    test_type: dict = None, sample_time: str = "1 second"
) -> dict:
    """
    Prepare the PyBaMM environment for running simulations.
    This function should be called before any PyBaMM simulation is run.
    It sets up the necessary parameters and configurations.
    """
    


    # Step 3d: Iterate over each simulation input (power or c_rate)
    def anode_potential_cutoff_function(variables):
        return (
            variables["Anode potential [V]"] - test_type["anode_potential_threshold_V"]
        )

    anode_potential_termination = pybamm.step.CustomTermination(
        name="Anode potential cut-off [V]",
        event_function=anode_potential_cutoff_function,
    )

    def jelly_roll_temperature_cutoff_function(variables):
        return (
            test_type["jelly_roll_temperature_threshold_K"]
            - variables["Volume-averaged cell temperature [K]"]
        )

    jelly_roll_temperature_termination = pybamm.step.CustomTermination(
        name="Jelly roll temperature cut-off [K]",
        event_function=jelly_roll_temperature_cutoff_function,
    )
    # Initialize PyBaMM
    if test_type["name"] == "DCIR":
        if "current_A" in test_type:
            experiment = pybamm.Experiment(
                [
                    ("Rest for 1 seconds"),
                    (
                        f"{test_type['direction'].capitalize()} at {test_type['current_A']}A for {test_type['duration_s']} seconds or until {test_type['voltage_limit_V']} V",
                        "Rest for 600 seconds",
                    ),
                ]
            )
        else:
            experiment = pybamm.Experiment(
                [
                    ("Rest for 1 seconds"),
                    (
                        f"{test_type['direction'].capitalize()} at {test_type['c_rate']}C for {test_type['duration_s']} seconds or until {test_type['voltage_limit_V']} V",
                        "Rest for 600 seconds",
                    ),
                ],
                period=sample_time,
            )
    elif test_type["name"] == "CAPACITY_MATCH":
        experiment: pybamm.Experiment = pybamm.Experiment(
            [
                (
                    "Rest for 1 seconds",
                    f"Charge at {test_type['cRate_ch']}C for 36000 seconds or until {test_type['voltage_max_V']} V",
                    f"Hold at {test_type['voltage_max_V']} V until 0.02C",
                ),
                ("Rest for 3600 seconds",),
                (
                    f"Discharge at {test_type['cRate_dis']}C for 360000 seconds or until {test_type['voltage_min_V']} V"
                ),
                ("Rest for 3600 seconds",),
            ],
            period=sample_time,
        )
    elif test_type["name"] == "POWER_TEST":
        # Perform a discharge simulation to set the nominal cell capacity
        experiment = pybamm.Experiment(
            [
                ("Rest for 1 seconds"),
                (
                    pybamm.step.power(
                        (
                            test_type["power_W"]
                            if test_type["direction"] == "discharge"
                            else -test_type["power_W"]
                        ),
                        duration=test_type["duration_s"],
                        termination=[
                            anode_potential_termination,
                            jelly_roll_temperature_termination,
                            f"{test_type['voltage_limit_V']}V",
                        ],
                        # skip_ok=False
                    ),
                ),
                ("Rest for 600 seconds",),
            ],
            period=sample_time,
        )
    elif test_type["name"] == "C_RATE_TEST":
        # Perform a discharge simulation to set the nominal cell capacity
        experiment = pybamm.Experiment(
            [
                ("Rest for 1 seconds"),
                (
                    pybamm.step.c_rate(
                        (
                            test_type["c_rate"]
                            if test_type["direction"] == "discharge"
                            else -test_type["c_rate"]
                        ),
                        duration=test_type["duration_s"],
                        termination=[
                            anode_potential_termination,
                            jelly_roll_temperature_termination,
                            f"{test_type['voltage_limit_V']}V",
                        ],
                    ),
                ),
                ("Rest for 3600 seconds",),
            ],
            period=sample_time,
        )
    else:
        experiment = pybamm.Experiment([test_type], period="1 second")
    return experiment

@mcp.tool()
def get_cell_dcir_tool_info():
    """
    Provides description and instructions on how to use the get_dcir tool.
    This tool should be called every time the get_dcir tool is used.
    Call setup_cell_models before get_dcir to initialize the cell simulation models.
    """
    return (
        "This function performs a battery simulation with the following features:\n"
        "- Calculates DCIR at a specified temperature, duration, and state of charge (SoC)\n"
        "- Runs a simulation to reach the specified SoC, then applies a pulse current for a specified duration\n"
        "- Uses the ORegan2022 parameter set by default, or Prada2013 for LFP\n"
        "- Implements voltage cut-off limits for safety\n"
        "- Can use modified cell design parameters\n"
        "\n"
        "Args:\n"
        "    pulse_current (float): Pulse current in amperes\n"
        "    pulse_direction (str, optional): Pulse direction ('discharge' or 'charge'). Defaults to 'discharge'.\n"
        "    pulse_duration (Union[float, list], optional): Pulse duration in seconds. Defaults to 10.0.\n"
        "    rest_duration (float, optional): Rest duration before pulse in seconds. Defaults to 600.0.\n"
        "    temperature (Union[float, list], optional): Ambient temperature in Kelvin. Defaults to 298.0.\n"
        "    soc (Union[float, list], optional): Initial state of charge (0-1). Defaults to 0.5.\n"
        '    direction (Direction, optional): "discharge" or "charge". Defaults to "discharge".\n'
        "    upper_voltage_cutoff (float, optional): Upper voltage cut-off in volts. Defaults to 4.2.\n"
        "    lower_voltage_cutoff (float, optional): Lower voltage cut-off in volts. Defaults to 2.8.\n"
        "    scale_ionic_conductivity (float, optional): Electrolyte ionic conductivity scale factor. Defaults to 1.0.\n"
        "\n"
        "Returns:\n"
        "    dict: Nested dictionary with DCIR values for each temperature, pulse duration, and SoC.\n"
        + TOOL_INFO_FOOTER
    )

@mcp.tool()
@with_timeout(TOOL_TIMEOUT)
def get_cell_dcir(
    user_id: Optional[str],
    cell_design_id: str,
    simulation_conditions: dict,
) -> dict:
    """
    Simulate battery performance to calculate dcir (direct current internal resistance) at a given SoC (state of charge) level.
    The get_dcir_tool_info tool should be called before this function.
    Get the active design from the session.
    Args:
        user_id: Automatically set by the MCP server.
        cell_design_id: Cell design stored in the session.
        simulation_conditions: A dictionary containing the simulation conditions.
        {
            c_rate: The c_rate for the pulse current (e.g., 1.0 for 1C). Either c_rate or current_A must be provided.
            current_A: The absolute pulse current in amperes. Either c_rate or current_A must be provided.
            direction: "discharge" or "charge". Defaults to "discharge".
            duration_s: Pulse duration in seconds. Can be a single float or a list of floats. Defaults to 10.0s.
            temperature_K: Ambient temperature in Kelvin. Can be a single float or a list of floats. Defaults to 298.15K (25°C).
            initial_soc: Initial state of charge (0-1). Can be a single float or a list of floats. Defaults to 0.5 (50%).
            upper_voltage_cutoff_V: Upper voltage cut-off in volts. If None, uses the value from the cell design.
            lower_voltage_cutoff_V: Lower voltage cut-off in volts. If None, uses the value from the cell design.
            cell_contact_resistance_Ohm: Contact resistance between cell and contact in ohms. Defaults to 1.0e-5.
        }
    Returns:
        A nested dictionary with DCIR values for each temperature, pulse duration, and SoC.
        dict: {'status': str, 'results': dict, 'message': str}

    """
    # Check if cell simulation model exists
    db_result = fetch_cell_design_from_db(
        user_id=user_id, cell_design_id=cell_design_id
    )
    if db_result.get("status", "failed") != "success":
        return {"status": "failed", "message": db_result.get("message")}
    cell_design = db_result["cell_design"]
    cell_design_parameters = cell_design["cell_design_parameters"]
    if "cell_simulation_models" not in cell_design:
        raise Exception("Cell simulation model not found in design. Please run setup_cell_models first.")
    
    models = cell_design["cell_simulation_models"]
    sim_parameters = {}
    sim_model = None
    model = None
    if "SPMeT" in models:
        sim_model = pybamm.lithium_ion.SPMe(
                options=models["SPMeT"].get("model_options", {})
            )
        model = "SPMeT"
    else:
        raise ValueError(
            "Invalid model type specified. Run setup_cell_models with model_type='SPMeT' to set up the SPMeT model."
        )  # Update model parameters with cell design parameters

    sim_parameters = pybamm.ParameterValues(
        models[model].get("default_parameter_set", "ORegan2022")
    )
    for key, value in cell_design["cell_simulation_models"][model][
        "optimized_parameters"
    ].items():
        sim_parameters.update({key: value}, check_already_exists=False)
    # Input conditions
    c_rate = simulation_conditions.get("c_rate", 1)
    current_A = simulation_conditions.get("current_A", None)
    if c_rate is None and current_A is None:
        raise Exception("Either c_rate or current_A must be provided.")
    direction = simulation_conditions.get("direction", "discharge")
    duration_s = simulation_conditions.get("duration_s", 10.0)
    temperature_K = simulation_conditions.get("temperature_K", 298.15)
    initial_soc = simulation_conditions.get("initial_soc", 0.5)
    upper_voltage_cutoff_V = simulation_conditions.get("upper_voltage_cutoff_V", None)
    lower_voltage_cutoff_V = simulation_conditions.get("lower_voltage_cutoff_V", None)
    cell_contact_resistance_Ohm = simulation_conditions.get("cell_contact_resistance_Ohm", 1.0e-5)
    # scale_ionic_conductivity = simulation_conditions.get(
    #     "scale_ionic_conductivity", 1.0
    # )
    # Validate inputs
    if direction.lower() not in ["discharge", "charge"]:
        raise Exception("Direction must be either 'discharge' or 'charge'.")
    if isinstance(duration_s, (list, tuple)):
        if any((not isinstance(d, (float, int)) or d <= 0) for d in duration_s):
            raise Exception("All durations must be positive numbers.")
    temperature_K = (
        [temperature_K] if isinstance(temperature_K, (float, int)) else temperature_K
    )
    out_dcir = {}
    error_msgs = []
    soc_list = [initial_soc] if isinstance(initial_soc, float) else initial_soc
    for T in temperature_K:
        try:
            sim_parameters.update(
                {"Ambient temperature [K]": T}, check_already_exists=False
            )
            sim_parameters.update(
                {"Initial temperature [K]": T}, check_already_exists=False
            )

            pulse_duration_list = (
                [duration_s] if isinstance(duration_s, (float, int)) else duration_s
            )
            if T not in out_dcir:
                out_dcir[T] = {}
            for dt in pulse_duration_list:
                try:
                    sim_pulse_duration = dt if dt > 1 else 1.0
                    expt_dict = {
                        "name": "DCIR",
                        "direction": direction.lower(),
                        "voltage_limit_V": (
                            (
                                upper_voltage_cutoff_V
                                if upper_voltage_cutoff_V is not None
                                else sim_parameters["Upper voltage cut-off [V]"]
                            )
                            if direction.lower() == "charge"
                            else (
                                lower_voltage_cutoff_V
                                if lower_voltage_cutoff_V is not None
                                else sim_parameters["Lower voltage cut-off [V]"]
                            )
                        ),
                        "duration_s": dt,
                    }
                    if current_A is not None:
                        expt_dict["current_A"] = current_A
                    else:
                        expt_dict["c_rate"] = c_rate
                    try:
                        experiment = prep_simulation_experiment(
                            expt_dict,
                            sample_time="0.01 second",
                        )

                        # Select model and solver based on power/energy ratio
                        # model_type = "SPMeT" if c_rate >= 1 else "DFN"
                        model_type = "SPMeT"

                        sim_model = (
                            pybamm.lithium_ion.DFN(
                                options=models[model_type].get("model_options")
                            )
                            if model_type == "DFN"
                            else pybamm.lithium_ion.SPMe(
                                options=models[model_type].get("model_options")
                            )
                        )
                        sim = pybamm.Simulation(
                        sim_model,
                        parameter_values=sim_parameters,
                        experiment=experiment,
                    )

                    except Exception as e:
                        error_msgs.append(
                            f"T={T}, dt={dt}, soc={soc_list}: Failed to prepare simulation experiment: {e}"
                        )
                        continue

                    if dt not in out_dcir[T]:
                        out_dcir[T][dt] = {}

                    for s in soc_list:
                        try:
                            if s < 0 or s > 1:
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: State of charge must be between 0 and 1."
                                )
                                continue
                            solver = pybamm.IDAKLUSolver(atol=1e-4, rtol=1e-4, output_variables=["Time [s]", "Terminal voltage [V]", "Current [A]", "Discharge capacity [A.h]", "Discharge energy [W.h]", "Throughput capacity [A.h]", "Throughput energy [W.h]", "Volume-averaged cell temperature [K]", "Power [W]"])
                            sim.solve(initial_soc=s, solver=solver)

                            # Robustly check cycles and entries
                            if (
                                not hasattr(sim.solution, "cycles")
                                or len(sim.solution.cycles) < 2
                            ):
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: Simulation did not produce enough cycles (expected at least 2)."
                                )
                                continue
                            cycle0 = sim.solution.cycles[0]
                            cycle1 = sim.solution.cycles[1]
                            # Check for required keys and non-empty entries
                            cycle0_tv = cycle0["Terminal voltage [V]"].entries
                            cycle1_tv = cycle1["Terminal voltage [V]"].entries
                            if len(cycle0_tv) == 0:
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: No entries in cycle 0 terminal voltage."
                                )
                                continue
                            if len(cycle1_tv) == 0:
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: No entries in cycle 1 terminal voltage."
                                )
                                continue
                            cycle1_time = cycle1["Time [s]"].entries
                            if len(cycle1_time) == 0:
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: No entries in cycle 1 time."
                                )
                                continue
                            time = cycle1_time - cycle1_time[0] + 0.01
                            V0 = cycle0_tv[-1]
                            pulse_end_idx = np.argmin(np.abs(time - sim_pulse_duration))
                            if pulse_end_idx >= len(cycle1_tv):
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: Pulse end index {pulse_end_idx} out of bounds for voltage array of length {len(cycle1_tv)}."
                                )
                                continue
                            V_pulse = cycle1_tv[pulse_end_idx]
                            delta_V = V0 - V_pulse
                            delta_I = (
                                abs(current_A)
                                if current_A is not None
                                else abs(c_rate)
                                * cell_design_parameters["Cell nominal capacity [A.h]"]
                            )
                            if delta_I == 0:
                                error_msgs.append(
                                    f"T={T}, dt={dt}, soc={s}: Delta current is zero, cannot compute DCIR."
                                )
                                continue
                            dcir = delta_V / delta_I
                            if s not in out_dcir[T][dt]:
                                out_dcir[T][dt][s] = {}
                            out_dcir[T][dt][s] = dcir + cell_contact_resistance_Ohm
                        except Exception as e:
                            error_msgs.append(f"T={T}, dt={dt}, soc={s}: {str(e)}")
                except Exception as e:
                    raise Exception(f"T={T}, dt={dt}: {str(e)}")
        except Exception as e:
            raise Exception(f"T={T}: {str(e)}")

    # Convert nested out_dcir to flat JSON format
    json_result = {
        "Temperature [K]": [],
        "SoC [%]": [],
        "Pulse Direction": [],
        "Pulse Current [A]": [],
        "Pulse Duration [s]": [],
        "DCIR [mOhm]": [],
    }
    for T, dt_dict in out_dcir.items():
        for dt, soc_dict in dt_dict.items():
            for s, dcir_val in soc_dict.items():
                json_result["Temperature [K]"].append(T)
                json_result["SoC [%]"].append(round(s * 100, 2))
                json_result["Pulse Direction"].append(direction)
                json_result["Pulse Current [A]"].append(
                    current_A
                    if current_A is not None
                    else abs(c_rate)
                    * cell_design_parameters["Cell nominal capacity [A.h]"]
                )
                json_result["Pulse Duration [s]"].append(dt)
                json_result["DCIR [mOhm]"].append(round(float(dcir_val) * 1e3, 3))

    update_cell_design_in_db(
        user_id=user_id,
        cell_design_id=cell_design_id,
        updates={
            "simulation_results": {
                "DCIR": {
                    "simulation_conditions": simulation_conditions,
                    "results": json_result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            },
        },
    )
    return {
        "status": "success",
        "results": json_result,
        "message": error_msgs if error_msgs else None,
    }

@mcp.tool()
def get_cell_power_tool_info() -> str:
    """
    Provides description and instructions on how to use the get_cell_power tool.
    This tool should be called every time the get_cell_power tool is used.
    Call setup_cell_models before get_cell_power to initialize the cell simulation models.
    *Always* adjust contact resistance using given power at 25degC as reference first while comparing to user provided power.
    """
    return (
        "This function simulates battery performance at multiple power levels, temperatures, and SOCs with power convergence.\n"
        "- Supports both charging and discharging scenarios with comprehensive validation\n"
        "- Implements nested loops: Temperature → SOC → Power correction\n"
        "- *Always* simulate one temperature at a time\n"
        "- Automatically adjusts power using binary search for optimal convergence\n"
        "- Implements voltage cut-off limits and lithium plating and thermal safety thresholds\n"
        "\n"
        "Required Args (via simulation_conditions dict):\n"
        "    power_W (float): Initial power in watts for the simulation (must be positive)\n"
        "    direction (str): Operation direction, either 'discharge' or 'charge'.\n"
        "    temperature_K (Union[float, list]): Ambient temperature(s) in Kelvin. Can be single value or list.\n"
        "    initial_soc (Union[float, list]): Initial state of charge (0-1). Can be single value or list.\n"
        "    duration_s (int): Target simulation duration in seconds. Defaults to 3600 (1 hour). Must be positive.\n"
        "\n"
        "Optional Args (via simulation_conditions dict):\n"
        "    upper_voltage_cutoff_V (float): Upper voltage cut-off for charging in volts. Defaults to 4.2.\n"
        "    lower_voltage_cutoff_V (float): Lower voltage cut-off for discharging in volts. Defaults to 2.8.\n"
        "    anode_potential_threshold_V (float): Anode potential threshold for lithium plating detection in volts. Defaults to 0.01.\n"
        "    jelly_roll_temperature_threshold_K (float): Maximum allowed jelly roll temperature in Kelvin. Defaults to 363.15.\n"
        "    thermal_paste_conductivity_W_mK (float): Thermal paste conductivity in W/(m·K). Defaults to 5.0.\n"
        "    thermal_paste_thickness_mm (float): Thermal paste thickness in mm. Defaults to 1.0.\n"
        "    cell_contact_resistance_Ohm (float): Contact resistance between cell and contact in ohms. Defaults to 1.0e-5.\n"
        "\n"
        "Returns:\n"
        "    dict: Nested dictionary with power values for each temperature, SOC, and optimized power level.\n"
        "    Format: {'status': str, 'results': dict, 'message': str}\n"
        "    Results include: Temperature [K], SoC [%], Direction, Initial Power [W], Final Power [W], Time [s], Termination Reason\n"
        "\n"
        "Termination Reasons:\n"
        "    - 'Time fulfilled!': Simulation completed successfully within duration\n"
        "    - 'Lithium plating detected!': Anode potential threshold reached\n"
        "    - 'Voltage limit reached!': Cell voltage hit cutoff limit\n"
        "    - 'High initial resistance detected!': Initial conditions issue\n"
        "    - 'Unknown termination reason!': Unexpected simulation termination\n"
        "\n" + TOOL_INFO_FOOTER
    )

@mcp.tool()
@with_timeout(TOOL_TIMEOUT)
def get_cell_power(
    user_id: Optional[str],
    cell_design_id: str,
    simulation_conditions: dict,
) -> dict:
    """
    Simulate battery performance at multiple power levels, temperatures, and SOCs with power convergence.
    The get_cell_power_tool_info tool should be called before this function.
    This function supports both charging and discharging scenarios with nested loops:
    1. Temperature loop (outermost)
    2. SOC loop (middle) 
    3. Power correction loop (innermost)

    Args:
        user_id (str): Automatically set by the MCP server.
        cell_design_id (str): Cell design identifier
        simulation_conditions (dict): Simulation parameters including power_W, temperature_K, etc.

    Returns:
        A nested dictionary with power values for each temperature, pulse duration, and SoC.
        dict: {'status': str, 'results': dict, 'message': str}
    """
    try:
        # Validate input parameters
        power_W = simulation_conditions.get("power_W")
        if power_W is None or power_W <= 0:
            return {"status": "failed", "message": "Power must be a positive number."}

        # Extract simulation conditions with defaults
        temperature_K = simulation_conditions.get("temperature_K", 298.15)
        initial_soc = simulation_conditions.get("initial_soc", 0.5)
        duration_s = simulation_conditions.get("duration_s", 3600)  # Default to 1 hour
        direction = simulation_conditions.get("direction", "discharge")
        upper_voltage_cutoff_V = simulation_conditions.get(
            "upper_voltage_cutoff_V", 4.2
        )
        lower_voltage_cutoff_V = simulation_conditions.get(
            "lower_voltage_cutoff_V", 2.8
        )
        anode_potential_threshold_V = simulation_conditions.get(
            "anode_potential_threshold_V", 0.01
        )
        jelly_roll_temperature_threshold_K = simulation_conditions.get(
            "jelly_roll_temperature_threshold_K", 363.15
        )
        thermal_paste_conductivity_W_mK = simulation_conditions.get(
            "thermal_paste_conductivity_W_mK", 5.0
        )
        thermal_paste_thickness_mm = simulation_conditions.get(
            "thermal_paste_thickness_mm", 1.0
        )
        cell_contact_resistance_Ohm = simulation_conditions.get("cell_contact_resistance_Ohm", 1.0e-5)

        # Validate ranges
        if direction not in ["charge", "discharge"]:
            raise ValueError("Direction must be 'charge' or 'discharge'.")

        # Fetch cell design from database
        db_result = fetch_cell_design_from_db(
            user_id=user_id, cell_design_id=cell_design_id
        )
        if db_result.get("status", "failed") != "success":
            raise Exception(db_result.get("message", "Failed to fetch cell design"))
        cell_design = db_result["cell_design"]
        cell_design_parameters = cell_design["cell_design_parameters"]
        if "cell_simulation_models" not in cell_design:
            raise Exception("Cell simulation model not found in design. Please run setup_cell_models first.")

        models = cell_design["cell_simulation_models"]

        # Calculate thermal parameters after fetching cell design
        h_ext = (
            1
            / (
                thermal_paste_thickness_mm
                * 1e-3
                / (
                    thermal_paste_conductivity_W_mK
                    * cell_design_parameters["Cell cooling surface area [mm2]"]
                    * 1e-6
                )
                + cell_design_parameters["Cell thermal resistance [K.W-1]"]
            )
            / cell_design_parameters["Cell cooling surface area [mm2]"]
            * 1e6
        )

        # Set the nominal cell energy based on the cell design parameters
        cell_reference_energy_Wh = cell_design_parameters["Cell nominal energy [W.h]"]

        # Prepare input lists for nested loops
        temperature_K = (
            [temperature_K] if isinstance(temperature_K, (float, int)) else temperature_K
        )
        initial_soc = (
            [initial_soc] if isinstance(initial_soc, (float, int)) else initial_soc
        )
        
        # Validate temperature values after list conversion
        if isinstance(temperature_K, (list, tuple)):
            if any(t <= 0 for t in temperature_K):
                raise ValueError("All temperatures must be positive.")
        else:
            if temperature_K <= 0:
                raise ValueError("Temperature must be positive.")
        
        # Initialize output structure
        out_power = {}
        error_msgs = []
        
        # Nested loops: Temperature → SOC → Power optimization
        for T in temperature_K:
            try:
                if T not in out_power:
                    out_power[T] = {}
                    
                for soc in initial_soc:
                    try:
                        if soc < 0 or soc > 1:
                            error_msgs.append(
                                f"T={T}, soc={soc}: State of charge must be between 0 and 1."
                            )
                            continue
                            
                        if soc not in out_power[T]:
                            out_power[T][soc] = {}
                        
                        # Binary search parameters for power optimization at this T and SOC
                        min_power_W = cell_reference_energy_Wh * 0.01  # Start with 1% of cell energy
                        max_power_W = cell_reference_energy_Wh * 20  # Allow up to 2000% of cell energy
                        tolerance = 0.01  # 1% tolerance for convergence
                        max_iterations = 20  # Maximum binary search iterations
                        
                        # Binary search to find the maximum working power
                        iteration = 0
                        best_working_power = None
                        best_time = 0.0
                        best_termination_reason = "Time fulfilled!"
                        
                        while iteration < max_iterations and (max_power_W - min_power_W) / max_power_W > tolerance:
                            iteration += 1
                            # Test middle power value
                            test_power_W = (min_power_W + max_power_W) / 2
                            
                            try:
                                # Extract scalar duration value once (can be list or scalar input)
                                # This consolidates the duration handling for both simulation and model selection
                                if isinstance(duration_s, (list, tuple)):
                                    duration_scalar = duration_s[0] if duration_s else 3600
                                else:
                                    duration_scalar = duration_s
                                
                                # Determine voltage limit based on direction
                                if direction.lower() == "charge":
                                    voltage_limit_V = (
                                        upper_voltage_cutoff_V
                                        if upper_voltage_cutoff_V is not None
                                        else cell_design_parameters["Upper voltage cut-off [V]"]
                                    )
                                else:
                                    voltage_limit_V = (
                                        lower_voltage_cutoff_V
                                        if lower_voltage_cutoff_V is not None
                                        else cell_design_parameters["Lower voltage cut-off [V]"]
                                    )

                                # Create simulation experiment
                                experiment = prep_simulation_experiment(
                                    {
                                        "name": "POWER_TEST",
                                        "direction": direction,
                                        "power_W": test_power_W,
                                        "duration_s": duration_scalar,
                                        "voltage_limit_V": voltage_limit_V,
                                        "anode_potential_threshold_V": anode_potential_threshold_V,
                                        "jelly_roll_temperature_threshold_K": jelly_roll_temperature_threshold_K,
                                    }
                                )

                                # Select model and solver based on power/energy ratio
                                power_ratio = int(test_power_W / cell_reference_energy_Wh)
                                # Use power ratio for model selection, with duration as secondary criterion
                                if power_ratio >= 1:
                                    model_type = "SPMeT"

                                # Find the appropriate model from the models list
                                sim_model = None
                                model_key = None
                                for model_key in models:
                                    if model_key == model_type:
                                        break
                                
                                if model_key is None:
                                    # Fallback to first available model
                                    model_key = list(models.keys())[0] if models else "SPMeT"
                                
                                # Create the simulation model
                                if model_type == "DFN":
                                    sim_model = pybamm.lithium_ion.DFN(
                                        options=models[model_key].get("model_options", {})
                                    )
                                else:
                                    sim_model = pybamm.lithium_ion.SPMe(
                                        options=models[model_key].get("model_options", {})
                                    )
                                                                
                                sim_model.variables["Anode potential [V]"] = sim_model.variables[
                                    "Negative electrode surface potential difference at separator interface [V]"
                                ]

                                # Set up simulation parameters
                                sim_parameters = pybamm.ParameterValues(
                                    models[model_key].get("default_parameter_set", "ORegan2022")
                                )
                                sim_parameters.update(
                                    {
                                        key: value
                                        for key, value in models[model_key][
                                            "optimized_parameters"
                                        ].items()
                                    },
                                    check_already_exists=False,
                                )
                                sim_parameters.update(
                                    {
                                        "Ambient temperature [K]": T,
                                        "Initial temperature [K]": T,
                                        "Total heat transfer coefficient [W.m-2.K-1]": h_ext,
                                        "Contact resistance [Ohm]": cell_contact_resistance_Ohm,
                                    }
                                )

                                # Create and run simulation
                                sim = pybamm.Simulation(
                                    sim_model,
                                    experiment=experiment,
                                    parameter_values=sim_parameters,
                                )
                                solver = pybamm.IDAKLUSolver(atol=1e-4, rtol=1e-4, output_variables=["Time [s]", "Terminal voltage [V]", "Current [A]", "Discharge capacity [A.h]", "Discharge energy [W.h]", "Throughput capacity [A.h]", "Throughput energy [W.h]", "Volume-averaged cell temperature [K]", "Power [W]"])
                                sim.solve(initial_soc=soc, solver=solver)
                                termination_reason = "Time fulfilled!"
                                # Check simulation results
                                if sim.solution and len(sim.solution.cycles) > 1:
                                    result_status = sim.solution.cycles[1].termination
                                    time_s = sim.solution.cycles[1]["Time [s]"].entries[-1]

                                    if result_status != "final time":
                                        termination_reason = sim.solution.cycles[1].termination
                                        result_status = "failed"
                                        # Binary search: reduce upper bound
                                        max_power_W = test_power_W
                                    else:
                                        result_status = "success"
                                        # Binary search: increase lower bound and update best result
                                        min_power_W = test_power_W
                                        if best_working_power is None or test_power_W > best_working_power:
                                            best_working_power = test_power_W
                                            best_time = time_s
                                            best_termination_reason = termination_reason
                                else:
                                    result_status = "failed"
                                    # Binary search: reduce upper bound
                                    max_power_W = test_power_W

                            except Exception as e:
                                result_status = "failed"
                                # Binary search: reduce upper bound on error
                                max_power_W = test_power_W
                                if iteration == max_iterations:
                                    error_msg = f"T={T}, soc={soc}: Simulation failed after {max_iterations} iterations. Last error: {str(e)}"
                                    error_msgs.append(error_msg)
                                    continue

                        # Store results for this T and SOC
                        if best_working_power is not None:
                            out_power[T][soc] = {
                                "power_W": best_working_power,
                                "time_s": best_time,
                                "termination_reason": best_termination_reason,
                                "status": "success"
                            }
                        else:
                            # Fall back to minimum power as last resort
                            out_power[T][soc] = {
                                "power_W": min_power_W,
                                "time_s": 0.0,
                                "termination_reason": "Failed to converge",
                                "status": "failed"
                            }
                            error_msgs.append(f"T={T}, soc={soc}: Failed to converge after {max_iterations} iterations.")

                    except Exception as e:
                        error_msgs.append(f"T={T}, soc={soc}: {str(e)}")
                        out_power[T][soc] = {
                            "power_W": 0.0,
                            "time_s": 0.0,
                            "termination_reason": f"Error: {str(e)}",
                            "status": "failed"
                        }

            except Exception as e:
                error_msgs.append(f"T={T}: {str(e)}")

        # Convert nested out_power to flat JSON format (similar to DCIR tool)
        json_result = {
            "Temperature [K]": [],
            "SoC [%]": [],
            "Direction": [],
            "Initial Power [W]": [],
            "Final Power [W]": [],
            "Time [s]": [],
            "Termination Reason": [],
            "Status": []
        }
        
        for T, soc_dict in out_power.items():
            for soc, power_data in soc_dict.items():
                json_result["Temperature [K]"].append(T)
                json_result["SoC [%]"].append(round(soc * 100, 2))
                json_result["Direction"].append(direction)
                json_result["Initial Power [W]"].append(power_W)  # Original input power
                json_result["Final Power [W]"].append(round(power_data["power_W"], 3))
                json_result["Time [s]"].append(round(power_data["time_s"], 3))
                json_result["Termination Reason"].append(power_data["termination_reason"])
                json_result["Status"].append(power_data["status"])

        # Update database with results
        try:
            update_cell_design_in_db(
                user_id=user_id,
                cell_design_id=cell_design_id,
                updates={
                    "simulation_results": {
                        "Power": {
                            "simulation_conditions": simulation_conditions,
                            "results": json_result,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    },
                },
            )
        except Exception as e:
            raise Exception(f"Failed to update database: {str(e)}")

    except Exception as e:
        raise Exception(f"Simulation execution failed: {str(e)}")
    
    return {
        "status": "success",
        "results": json_result,
        "message": error_msgs if error_msgs else None,
    }
    
@mcp.tool()
def check_cell_performance_tool_info() -> str:
    """
    Provides description and instructions on how to use the check_cell_performance tool.
    This tool should be called every time the check_cell_performance tool is used.
    Call setup_cell_models before check_cell_performance to initialize the cell simulation models.
    """
    return (
        "This function simulates battery capacity and energy at a given power level or C-rate and returns the results.\n"
        "- *Never* set the simulation duration unless the user explicitly asks for it.\n"
        "- Supports both power-based and C-rate-based simulations with comprehensive validation\n"
        "- Estimates realistic cell capacity and energy at specified conditions\n"
        "- Implements voltage cut-off limits and thermal safety thresholds\n"
        "- Robust error handling with detailed failure messages\n"
        "\n"
        "Required Args (via simulation_conditions dict - provide EITHER power_W OR c_rate, not both):\n"
        "    power_W (float): Power in watts for the simulation (must be positive)\n"
        "    OR\n"
        "    c_rate (float): C-rate for the simulation (must be positive)\n"
        "    direction (str): Operation direction, either 'discharge' or 'charge'. Defaults to 'discharge'.\n"
        "    initial_soc (float): Initial state of charge (0-1). Defaults to 1. Must be between 0 and 1.\n"
        "    temperature_K (float): Ambient temperature in Kelvin. Defaults to 298.15. Must be positive.\n"
        "\n"
        "Optional Args (via simulation_conditions dict):\n"
        "    duration_s (int): Target simulation duration in seconds. Defaults to None for full charge/discharge.\n"
        "    upper_voltage_cutoff_V (float): Upper voltage cut-off for charging in volts. Defaults to 4.2.\n"
        "    lower_voltage_cutoff_V (float): Lower voltage cut-off for discharging in volts. Defaults to 2.8.\n"
        "    anode_potential_threshold_V (float): Anode potential threshold for lithium plating detection in volts. Defaults to 0.01.\n"
        "    jelly_roll_temperature_threshold_K (float): Maximum allowed jelly roll temperature in Kelvin. Defaults to 363.15.\n"
        "    thermal_paste_conductivity_W_mK (float): Thermal paste conductivity in W/(m·K). Defaults to 5.0.\n"
        "    thermal_paste_thickness_mm (float): Thermal paste thickness in mm. Defaults to 1.0.\n"
        "    cell_contact_resistance_Ohm (float): Contact resistance between cell and contact in ohms. Defaults to 1.0e-5.\n"
        "\n"
        "Returns:\n"
        "    dict: {'status': str, 'results': dict, 'message': str}\n"
        "        - status (str): 'success' or 'failed'\n"
        "        - results (optional, dict): For failure: error details with 'message' key\n"
        "        - message (str): Error message for failure\n"
        "\n"
        "Use Cases:\n"
        "    - Identify realistic cell gravimetric and volumetric energy density\n"
        "    - Evaluate capacity and energy at different power levels or C-rates\n"
        "    - Compare performance across different operating conditions\n"
        "    - Assess thermal behavior during operation\n"
        "\n" + TOOL_INFO_FOOTER
    )

@mcp.tool()
@with_timeout(TOOL_TIMEOUT)
def check_cell_performance(
    user_id: Optional[str],
    cell_design_id: str,
    simulation_conditions: dict,
) -> dict:
    """
    Simulate cell capacity and energy at a given power level or c_rate and return the results.
    *Always* call the check_cell_performance_tool_info tool before this function.

    Args:
        user_id (str): Automatically set by the MCP server.
        cell_design_id (str): Cell design identifier
        simulation_conditions (dict): Simulation parameters including power_W or c_rate, temperature_K, etc.

    Returns:
        dict: {'status': str, 'results': dict, 'message': str}
    """
    try:
        # Fetch cell design from database
        db_result = fetch_cell_design_from_db(
            user_id=user_id, cell_design_id=cell_design_id
        )
        if db_result.get("status", "failed") != "success":
            raise Exception(db_result.get("message", "Failed to fetch cell design"))
        cell_design = db_result["cell_design"]
        cell_design_parameters = cell_design["cell_design_parameters"]
        if "cell_simulation_models" not in cell_design:
            raise Exception("Cell simulation model not found in design. Please run setup_cell_models first.")

        # Extract simulation conditions
        power_W = simulation_conditions.get("power_W")
        c_rate = simulation_conditions.get("c_rate")
        initial_soc = simulation_conditions.get("initial_soc")
        direction = simulation_conditions.get("direction")
        temperature_K = simulation_conditions.get("temperature_K")
        duration_s = simulation_conditions.get("duration_s", None)
        upper_voltage_cutoff_V = simulation_conditions.get("upper_voltage_cutoff_V", cell_design_parameters["Upper voltage cut-off [V]"])
        lower_voltage_cutoff_V = simulation_conditions.get("lower_voltage_cutoff_V", cell_design_parameters["Lower voltage cut-off [V]"])
        anode_potential_threshold_V = simulation_conditions.get("anode_potential_threshold_V", 0.01)
        jelly_roll_temperature_threshold_K = simulation_conditions.get("jelly_roll_temperature_threshold_K", 363.15)
        thermal_paste_conductivity_W_mK = simulation_conditions.get("thermal_paste_conductivity_W_mK", 5.0)
        thermal_paste_thickness_mm = simulation_conditions.get("thermal_paste_thickness_mm", 1.0)
        cell_contact_resistance_Ohm = simulation_conditions.get("cell_contact_resistance_Ohm", 1.0e-5)
        
        # Validate input parameters
        if (power_W is None and c_rate is None) or (
            power_W is not None and c_rate is not None
        ):
            raise ValueError("Either power_W or c_rate must be provided, but not both.")

        if power_W is not None and power_W <= 0:
            raise ValueError("Power must be a positive number.")
        if c_rate is not None and c_rate <= 0:
            raise ValueError("c_rate must be a positive number.")
        if initial_soc is None or initial_soc < 0 or initial_soc > 1:
            raise ValueError("Initial SOC must be provided. It must be between 0 and 1. For full discharge, set to 1 and for full charge, set to 0.")
        if temperature_K is None or temperature_K <= 0:
            raise ValueError("Temperature must be positive.")
        if duration_s is not None and duration_s <= 0:
            raise ValueError("Duration must be positive.")
        if direction is None or direction not in ["charge", "discharge"]:
            raise ValueError("Direction must be 'charge' or 'discharge'.")
        if cell_contact_resistance_Ohm is None or cell_contact_resistance_Ohm <= 0:
            raise ValueError("Contact resistance must be a positive number.")
        # Calculate thermal parameters
        h_ext = (
            1
            / (
                thermal_paste_thickness_mm
                * 1e-3
                / (
                    thermal_paste_conductivity_W_mK
                    * cell_design_parameters["Cell cooling surface area [mm2]"]
                    * 1e-6
                )
                + cell_design_parameters["Cell thermal resistance [K.W-1]"]
            )
            / cell_design_parameters["Cell cooling surface area [mm2]"]
            * 1e6
        )

        # Set the nominal cell energy
        cell_reference_energy_Wh = cell_design_parameters["Cell nominal energy [W.h]"]

        # Determine simulation mode and value
        if power_W is not None:
            mode = "power"
            val = power_W
            # power_ratio = int(val / cell_reference_energy_Wh)
            # use_spm = power_ratio >= 1
        else:
            mode = "c_rate"
            val = c_rate
            # use_spm = val >= 0.33

        if duration_s is None:
            if mode == "power":
                duration_s = max(3600, int(1.2 * 3600 * cell_reference_energy_Wh / power_W))
            else:
                duration_s = max(3600, int(1.2 * 3600 / c_rate))

        # Output category
        category = "C_rate performance" if mode == "c_rate" else "Power performance"

        # Determine voltage limit based on direction
        if direction.lower() == "charge":
            voltage_limit_V = upper_voltage_cutoff_V
        else:
            voltage_limit_V = lower_voltage_cutoff_V

        # Select model and solver
        models = cell_design["cell_simulation_models"]

        model_type = "SPMeT"
        # DFN model is no longer supported
        sim_model = pybamm.lithium_ion.SPMe(options=models[model_type].get("model_options"))
        # sim_model = (
            # pybamm.lithium_ion.SPMeT(options=models[model_type].get("model_options"))
            # if model_type == "DFN"
            # else pybamm.lithium_ion.SPMe(options=models[model_type].get("model_options"))
        # )
        sim_model.variables["Anode potential [V]"] = sim_model.variables[
            "Negative electrode surface potential difference at separator interface [V]"
        ]

        # Set up simulation parameters
        sim_parameters = pybamm.ParameterValues(
            models[model_type].get("default_parameter_set")
        )
        sim_parameters.update(
            {
                key: value
                for key, value in models[model_type]["optimized_parameters"].items()
            },
            check_already_exists=False,
        )
        sim_parameters.update(
            {
                "Ambient temperature [K]": temperature_K,
                "Initial temperature [K]": temperature_K,
                "Total heat transfer coefficient [W.m-2.K-1]": round(h_ext, 3),
                "Contact resistance [Ohm]": cell_contact_resistance_Ohm,
            }
        )
        # Create experiment
        experiment_config = {
            "name": f"{mode.upper()}_TEST",
            "direction": direction,
            "duration_s": duration_s,
            "voltage_limit_V": voltage_limit_V,
            "anode_potential_threshold_V": anode_potential_threshold_V,
            "jelly_roll_temperature_threshold_K": jelly_roll_temperature_threshold_K,
        }

        if mode == "power":
            experiment_config["power_W"] = val
        else:
            experiment_config["c_rate"] = val

        experiment = prep_simulation_experiment(experiment_config)

        # Create and run simulation
        sim = pybamm.Simulation(
            sim_model,
            experiment=experiment,
            parameter_values=sim_parameters,
        )

        try:
            solver = pybamm.IDAKLUSolver(atol=1e-3, rtol=1e-3, output_variables=["Time [s]", "Terminal voltage [V]", "Current [A]", "Discharge capacity [A.h]", "Discharge energy [W.h]", "Throughput capacity [A.h]", "Throughput energy [W.h]", "Volume-averaged cell temperature [K]", "Power [W]"])
            soln = sim.solve(initial_soc=initial_soc, solver=solver)

            if not soln or len(soln.cycles) < 2:
                raise Exception("Simulation failed to produce valid results.")

            termination_reason = soln.cycles[1].termination
            if "initial" in termination_reason.lower():
                raise Exception("Simulation failed due to initial conditions.")

            # Extract results
            cycle_data = soln.cycles[1]
            final_time = round(float(cycle_data["Time [s]"].entries[-1]), 3)
            final_capacity = round(
                float(
                    cycle_data["Discharge capacity [A.h]"].entries[-1]
                    if direction == "discharge"
                    else cycle_data["Throughput capacity [A.h]"].entries[-1]
                ),
                3,
            )
            final_energy = round(
                float(
                    cycle_data["Discharge energy [W.h]"].entries[-1]
                    if direction == "discharge"
                    else cycle_data["Throughput energy [W.h]"].entries[-1]
                ),
                3,
            )

            # Prepare results
            json_result = {
                "Direction": direction.capitalize(),
                f"{mode.capitalize()}": val,
                "Temperature [degC]": temperature_K - 273.15,
                "Final time [s]": final_time,
                "Capacity [A.h]": round(final_capacity, 3),
                "Energy [W.h]": round(final_energy, 3),
                "Termination reason": termination_reason,
            }
            inner_termination_reason = sim.solution.termination
            if "initial" in inner_termination_reason:
                raise Exception(f"Simulation failed due to initial conditions. {inner_termination_reason}")

            # Build output DataFrame
            out_df = pd.DataFrame(
                {
                    "Time [s]": np.concatenate(
                        [
                            soln.cycles[0]["Time [s]"].entries[-1:],
                            soln.cycles[1]["Time [s]"].entries,
                        ]
                    ),
                    "Voltage [V]": np.concatenate(
                        [
                            soln.cycles[0]["Terminal voltage [V]"].entries[-1:],
                            soln.cycles[1]["Terminal voltage [V]"].entries,
                        ]
                    ),
                    "Current [A]": np.concatenate(
                        [
                            soln.cycles[0]["Current [A]"].entries[-1:],
                            soln.cycles[1]["Current [A]"].entries,
                        ]
                    ),
                    "Temperature [K]": np.concatenate(
                        [
                            soln.cycles[0][
                                "Volume-averaged cell temperature [K]"
                            ].entries[-1:],
                            soln.cycles[1][
                                "Volume-averaged cell temperature [K]"
                            ].entries,
                        ]
                    ),
                    "Power [W]": np.concatenate(
                        [
                            soln.cycles[0]["Power [W]"].entries[-1:],
                            soln.cycles[1]["Power [W]"].entries,
                        ]
                    ),
                }
            )
            if direction == "discharge":
                out_df["Capacity [A.h]"] = np.concatenate(
                    [
                        soln.cycles[0]["Discharge capacity [A.h]"].entries[-1:],
                        soln.cycles[1]["Discharge capacity [A.h]"].entries,
                    ]
                )
                out_df["Energy [W.h]"] = np.concatenate(
                    [
                        soln.cycles[0]["Discharge energy [W.h]"].entries[-1:],
                        soln.cycles[1]["Discharge energy [W.h]"].entries,
                    ]
                )
            else:
                out_df["Capacity [A.h]"] = np.concatenate(
                    [
                        soln.cycles[0]["Throughput capacity [A.h]"].entries[-1:],
                        soln.cycles[1]["Throughput capacity [A.h]"].entries,
                    ]
                )
                out_df["Throughput energy [W.h]"] = np.concatenate(
                    [
                        soln.cycles[0]["Throughput energy [W.h]"].entries[-1:],
                        soln.cycles[1]["Throughput energy [W.h]"].entries,
                    ]
                )
            out_df.reset_index(drop=True, inplace=True)
            out_df["Time [s]"] -= out_df["Time [s]"].iloc[0]
            out_df["Capacity [A.h]"] -= out_df["Capacity [A.h]"].iloc[0]
            if "Energy [W.h]" in out_df:
                out_df["Energy [W.h]"] -= out_df["Energy [W.h]"].iloc[0]
            # Use rdp to reduce the size of the dataframe
            out_df = out_df.round(3)
            
            # Apply RDP algorithm to reduce data points while preserving curve shape
            # Use Time vs Voltage for the main curve simplification
            if len(out_df) > 100:  # Only apply RDP if we have enough points
                try:
                    # Create coordinate points from Time and Voltage columns
                    time_voltage_points = out_df[["Time [s]", "Terminal voltage [V]"]].values
                    # Apply RDP to get simplified indices
                    simplified_indices = rdp.rdp(time_voltage_points, epsilon=0.0005, return_mask=True)
                    # Filter the DataFrame using the simplified indices
                    out_df = out_df.iloc[simplified_indices]
                except Exception as e:
                    # If RDP fails, keep the original data
                    logger.warning(f"RDP simplification failed: {e}. Using original data.")
            json_result_data = json_result.copy()
            json_result_data.update(out_df.to_dict(orient="list"))

            # Update database with results
            try:
                update_cell_design_in_db(
                    user_id=user_id,
                    cell_design_id=cell_design_id,
                    updates={
                        "simulation_results": {
                            f"{category}": {
                                "simulation_conditions": simulation_conditions,
                                "results": json_result_data,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        },
                    },
                )
            except Exception as e:
                raise Exception(f"Failed to update database: {str(e)}")

            return {
                "status": "success",
                "results": json_result,
                "message": "Simulation completed successfully.",
            }

        except Exception as e:
            raise Exception(f"Simulation execution failed: {str(e)}")

    except Exception as e:
        raise Exception(f"Simulation execution failed: {str(e)}")
    
# =========================================================================
# Simulation Execution and Plotting Tools
# =========================================================================

# @mcp.tool()
# def run_simulation_experiment(
#     cell_design_id: str,
#     experiment_description: str,
#     user_id: str = "aris-internal",
#     sample_time: str = "1 second"
# ) -> dict:
#     """
#     Convert natural language experiment description to PyBaMM experiment and execute simulation.
    
#     Args:
#         cell_design_id: Database ID of the cell design to simulate
#         experiment_description: Natural language description of the experiment to run
#         user_id: User ID for the simulation
#         sample_time: Sampling time for the simulation
        
#     Returns:
#         Dictionary with simulation results and status
#     """
#     try:
#         # First fetch the cell design
#         design_result = fetch_cell_design_from_db(
#             user_id=user_id,
#             cell_design_id=cell_design_id,
#             include_simulations=False
#         )
        
#         if design_result.get("status") != "success":
#             return {
#                 "status": "failed",
#                 "message": f"Failed to fetch cell design: {design_result.get('message', 'Unknown error')}"
#             }
        
#         # Parse experiment description to extract parameters
#         # This is a simplified parser - in practice, you might use more sophisticated NLP
#         experiment_description = experiment_description.lower()
        
#         # Default configuration
#         test_config = {
#             "name": "CUSTOM_EXPERIMENT",
#             "direction": "discharge",
#             "c_rate": 1.0,
#             "duration_s": 3600,
#             "voltage_limit_V": 2.5,
#             "anode_potential_threshold_V": 0.0,
#             "jelly_roll_temperature_threshold_K": 333.15,
#         }
        
#         # Parse direction
#         if "charge" in experiment_description:
#             test_config["direction"] = "charge"
#         elif "discharge" in experiment_description:
#             test_config["direction"] = "discharge"
        
#         # Parse C-rate
#         import re
#         c_rate_match = re.search(r'(\d+(?:\.\d+)?)\s*c', experiment_description)
#         if c_rate_match:
#             test_config["c_rate"] = float(c_rate_match.group(1))
        
#         # Parse duration
#         duration_match = re.search(r'(\d+)\s*(?:hour|hr|h)', experiment_description)
#         if duration_match:
#             test_config["duration_s"] = int(duration_match.group(1)) * 3600
#         else:
#             duration_match = re.search(r'(\d+)\s*(?:minute|min|m)', experiment_description)
#             if duration_match:
#                 test_config["duration_s"] = int(duration_match.group(1)) * 60
        
#         # Parse voltage limits
#         voltage_match = re.search(r'(\d+(?:\.\d+)?)\s*v', experiment_description)
#         if voltage_match:
#             test_config["voltage_limit_V"] = float(voltage_match.group(1))
        
#         # Parse temperature limits
#         temp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:celsius|c|°c)', experiment_description)
#         if temp_match:
#             temp_celsius = float(temp_match.group(1))
#             test_config["jelly_roll_temperature_threshold_K"] = temp_celsius + 273.15
        
#         # Determine test type based on description
#         if "dcir" in experiment_description or "internal resistance" in experiment_description:
#             test_config["name"] = "DCIR"
#         elif "capacity" in experiment_description:
#             test_config["name"] = "CAPACITY_MATCH"
#         elif "power" in experiment_description:
#             test_config["name"] = "POWER_TEST"
#         elif "c-rate" in experiment_description or "rate" in experiment_description:
#             test_config["name"] = "C_RATE_TEST"
        
#         # Run the simulation using the existing prep_simulation_experiment
#         simulation_result = prep_simulation_experiment(
#             test_type=test_config,
#             sample_time=sample_time
#         )
        
#         return {
#             "status": "success",
#             "cell_design_id": cell_design_id,
#             "experiment_description": experiment_description,
#             "parsed_config": test_config,
#             "simulation_result": simulation_result,
#             "message": f"Custom simulation completed successfully for design {cell_design_id}"
#         }
        
#     except Exception as e:
#         return {
#             "status": "failed",
#             "message": f"Simulation execution failed: {str(e)}"
#         }

# =========================================================================
# Main execution block
# =========================================================================

if __name__ == "__main__":
    
    # Check if running as HTTP server or stdio
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run as HTTP server using FastMCP's streamable HTTP with Uvicorn
        logger.info("Starting Cell Design MCP HTTP Server on port 9004")
        logger.info("Server will be accessible at http://0.0.0.0:9004")
        logger.info("LibreChat can connect via: http://host.docker.internal:9004")
        
        # Create the FastMCP streamable HTTP app
        app = mcp.streamable_http_app()
        
        # Start Uvicorn server with the app and extended timeouts for long-running PyBaMM simulations
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=9004, 
            log_level="info",
            timeout_keep_alive=int(os.getenv("UVICORN_TIMEOUT_KEEP_ALIVE", "300")),  # 5 minutes default
            timeout_graceful_shutdown=int(os.getenv("UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", "30")),  # 30 seconds default
            limit_max_requests=int(os.getenv("UVICORN_MAX_REQUESTS", "1000")),  # Max requests per worker
            limit_concurrency=int(os.getenv("UVICORN_CONCURRENCY_LIMIT", "100")),  # Max concurrent connections - increased from 10
        )
    else:
        # Default stdio transport for internal use
        mcp.run()
