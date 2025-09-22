"""
Cell Design Tools - Regular Python functions converted from MCP tools
"""

import hashlib
import json
import sys
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from google.adk.tools.function_tool import FunctionTool

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_server.cell_designer.cell_design import CellDesign, POSITIVE_ELECTRODE_MASS_LOADING_MIN, POSITIVE_ELECTRODE_MASS_LOADING_MAX
from mcp_server.cell_designer.electrode_formulation import KNOWN_FORMULATIONS, ElectrodeFormulation
from mcp_server.cell_designer.mongodb_interface import get_mongodb_storage
from mcp_server.tools import extract_keywords_from_parameters, generate_context_description
from .database_tools import store_cell_design_in_db, search_cell_designs_in_db, fetch_cell_design_from_db

# Global list of valid cell design parameter aliases
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
    "Negative electrode formulation.Primary binder",
    "Negative electrode formulation.Secondary binder",
    "Negative electrode formulation.Primary active material",
    "Negative electrode formulation.Primary binder mass fraction",
    "Negative electrode formulation.Secondary binder mass fraction",
    "Negative electrode formulation.Electrode specific capacity [mAh.g-1]",
    "Negative electrode formulation.Primary active material mass fraction",
    "Positive electrode formulation.Primary binder",
    "Positive electrode formulation.Primary active material",
    "Positive electrode formulation.Primary conductive agent",
    "Positive electrode formulation.Primary binder mass fraction",
    "Positive electrode formulation.Electrode specific capacity [mAh.g-1]",
    "Positive electrode formulation.Primary active material mass fraction",
    "Positive electrode formulation.Primary conductive agent mass fraction",
    # Can material attributes
    "Cell casing material.Name",
    "Cell casing material.Specific heat capacity [J.kg-1.K-1]",
    "Cell casing material.Density [g.cm-3]",
    "Cell casing material.Thermal conductivity [W.m-1.K-1]",
]


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


def get_cell_design(
    cell_design_parameters: dict,
    target_specifications: dict = None,
    force_store: bool = False,
    user_id: str = "default_user",
    session_id: str = None,
) -> dict:
    """
    Create and stores a cell design based on the specified cell design parameters and target specifications.
    Keep on optimizing the design within 1% tolerances of the target specifications.
    
    Args:
        cell_design_parameters: Dictionary of key cell design parameters to create the design
        target_specifications: Dictionary of target specifications to optimize against
        force_store: If True, the design will be stored even if it already exists in the database
        user_id: User ID for the design
        session_id: Session ID for the design
        
    Returns:
        A dictionary containing the status of cell design optimization, id of the design stored in the database, and any error messages.
    """
    # Use the global list of valid aliases
    valid_aliases = set(VALID_CELL_DESIGN_ALIASES)
    
    if target_specifications is None:
        target_specifications = {}
    
    # Check for invalid keys
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
    for key in ["Positive electrode formulation", "Negative electrode formulation"]:
        if key in cell_design_parameters:
            formulation_data = cell_design_parameters[key]
            if isinstance(formulation_data, str):
                try:
                    ef = ElectrodeFormulation(formulation_data)
                    cell_design_parameters[key] = ef.as_alias_dict()
                except ValueError as e:
                    raise ValueError(
                        f"Invalid formulation '{formulation_data}' for {key}. "
                        f"Error: {str(e)}"
                    )
            elif isinstance(formulation_data, dict):
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

    # Validate design against targets if provided
    for key in target_specifications:
        if "capacity" in key.lower():
            # Check if the design meets the capacity target
            if not (
                target_specifications[key] * 0.99
                < result["Cell nominal capacity [A.h]"]
                < target_specifications[key] * 1.01
            ):
                current_pos_ml = result['Positive electrode mass loading [mg.cm-2]']
                target_pos_ml = target_specifications[key]/result['Cell nominal capacity [A.h]']*result['Positive electrode mass loading [mg.cm-2]']
                
                MSG_OUT = f"Consider changing the positive electrode mass loading from {current_pos_ml} to {target_pos_ml} to meet the target."
                
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
        output["message"] = f"New design stored with ID {output['cell_design_id']}."
    else:
        raise Exception(f"Failed to store design: {output.get('message', 'unknown error')}")
        
    return output


def estimate_bill_of_materials(
    user_id: str = "default_user", 
    cell_design_id: str = None,
    cell_design_parameters: dict = None
) -> dict:
    """
    Estimate bill of materials for a battery cell design including component weights down to active material powders.
    *Always* check if the cell design exists in the database by calling fetch_cell_design_from_db.
    If it does not, use the cell_design_parameters to create a new cell design.
    
    Args:
        user_id: User ID for the design
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
        if db_result.get("status") != "success":
            return {"status": "failed", "message": "Cell design not found"}
        cell_design_parameters = db_result["cell_design"]["cell_design_parameters"]

    try:
        # Create CellDesign object for BOM calculation
        cell_design = CellDesign.from_overrides({})
        
        # Update with provided parameters
        for key, value in cell_design_parameters.items():
            if hasattr(cell_design, key.replace(' ', '_').replace('[', '_').replace(']', '').replace('-', '_').replace('.', '_')):
                setattr(cell_design, key.replace(' ', '_').replace('[', '_').replace(']', '').replace('-', '_').replace('.', '_'), value)

        # Calculate basic BOM components
        bom = {
            "total_cell_mass_g": cell_design_parameters.get("Cell mass [g]", 0),
            "positive_electrode": {
                "active_material_mass_g": 0,
                "binder_mass_g": 0,
                "conductive_agent_mass_g": 0,
                "current_collector_mass_g": 0,
            },
            "negative_electrode": {
                "active_material_mass_g": 0,
                "binder_mass_g": 0,
                "conductive_agent_mass_g": 0,
                "current_collector_mass_g": 0,
            },
            "separator_mass_g": 0,
            "electrolyte_mass_g": 0,
            "casing_mass_g": 0,
        }

        # Calculate electrode masses if formulations are available
        if "Positive electrode formulation" in cell_design_parameters:
            pos_form = cell_design_parameters["Positive electrode formulation"]
            pos_coating_mass = cell_design_parameters.get("Positive electrode coating mass [g]", 10)
            
            if isinstance(pos_form, dict):
                bom["positive_electrode"]["active_material_mass_g"] = pos_coating_mass * pos_form.get("Primary active material mass fraction", 0.95)
                bom["positive_electrode"]["binder_mass_g"] = pos_coating_mass * pos_form.get("Primary binder mass fraction", 0.03)
                bom["positive_electrode"]["conductive_agent_mass_g"] = pos_coating_mass * pos_form.get("Primary conductive agent mass fraction", 0.02)

        if "Negative electrode formulation" in cell_design_parameters:
            neg_form = cell_design_parameters["Negative electrode formulation"]
            neg_coating_mass = cell_design_parameters.get("Negative electrode coating mass [g]", 8)
            
            if isinstance(neg_form, dict):
                bom["negative_electrode"]["active_material_mass_g"] = neg_coating_mass * neg_form.get("Primary active material mass fraction", 0.95)
                bom["negative_electrode"]["binder_mass_g"] = neg_coating_mass * neg_form.get("Primary binder mass fraction", 0.05)

        return {
            "status": "success",
            "bill_of_materials": bom,
            "message": "Bill of materials calculated successfully"
        }

    except Exception as e:
        return {
            "status": "failed", 
            "message": f"Failed to calculate BOM: {str(e)}"
        }


def predict_cell_chemistry(
    nominal_voltage: float,
    volumetric_energy_density: float,
    gravimetric_energy_density: float
) -> str:
    """
    Predict battery cell chemistry based on performance characteristics.
    
    Args:
        nominal_voltage: Nominal voltage in V
        volumetric_energy_density: Volumetric energy density in Wh/L
        gravimetric_energy_density: Gravimetric energy density in Wh/kg
        
    Returns:
        String with predicted chemistry and confidence level
    """
    try:
        # Load the trained model
        model_path = Path(__file__).parent.parent.parent / "mcp_server" / "models" / "battery_chemistry_model.joblib"
        if not model_path.exists():
            return "Error: Chemistry prediction model not found"
            
        model = joblib.load(model_path)
        
        # Prepare input data
        input_data = [[nominal_voltage, volumetric_energy_density, gravimetric_energy_density]]
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


# Create FunctionTool wrappers for ADK
get_valid_cell_design_aliases_tool = FunctionTool(get_valid_cell_design_aliases)
get_cell_design_tool_info_tool = FunctionTool(get_cell_design_tool_info)
get_cell_design_tool = FunctionTool(get_cell_design)
estimate_bill_of_materials_tool = FunctionTool(estimate_bill_of_materials)
predict_cell_chemistry_tool = FunctionTool(predict_cell_chemistry)