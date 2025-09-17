import json
from google.adk.agents.callback_context import CallbackContext

import logging
import warnings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")


def _set_initial_states(callback_context: CallbackContext):
    """
    Sets up the initial state.
    Set this as a callback as before_agent_call of the root_agent.
    This gets called before the system instruction is contructed.

    Args:
        callback_context: The callback context.
    """
    if "cell_design_library" not in callback_context.state.to_dict():
        callback_context.state.update(
            {
                "cell_design_library": {
                    "cell_design_list": [],
                    "total_cell_designs_in_session": 0,
                    "active_cell_design_id": None,
                }
            }
        )
    logging.info(f"Loading Initial State: {callback_context.state.to_dict()}")


def _update_internal_state(
    callback_context: CallbackContext,
):
    """Update internal state with cell design."""
    if "cell_design_output" not in callback_context.state:
        logging.warning("No cell_design_output found in state to update.")
        return
    else:
        if callback_context.state["cell_design_output"] is None:
            logging.warning("cell_design_output is None.")
            return
        cell_design_output = callback_context.state.get("cell_design_output", "")
    if not cell_design_output:
        logging.warning("cell_design_output is empty.")
        return
    else:
        logging.info(f"cell_design_output: {cell_design_output}")
        try:
            cell_design_json = json.loads(cell_design_output)
        except json.JSONDecodeError as e:
            logging.error(f"cell_design_output is not valid JSON: {e}")
            return
        if (
            not isinstance(cell_design_json, dict)
            or "cell_design" not in cell_design_json
        ):
            logging.error("cell_design_output JSON does not contain 'cell_design' key.")
            return
        cell_design = cell_design_json["cell_design"]
        if "cell_design_library" not in callback_context.state:
            callback_context.state["cell_design_library"] = {
                "cell_design_list": [],
                "total_cell_designs_in_session": 0,
                "active_cell_design_id": None,
            }
        elif "cell_design_list" not in callback_context.state["cell_design_library"]:
            callback_context.state["cell_design_library"]["cell_design_list"] = []
        else:
            for design in callback_context.state["cell_design_library"][
                "cell_design_list"
            ]:
                logger.info(f"Checking design with ID: {design}")
                if "id" in design:
                    if design["id"] == cell_design["id"]:
                        logging.info(
                            f"Design with ID {design['id']} already exists. Skipping append."
                        )
                        return
        callback_context.state["cell_design_library"]["cell_design_list"].append(
            cell_design
        )
        callback_context.state["cell_design_library"][
            "total_cell_designs_in_session"
        ] += 1
        callback_context.state["cell_design_library"]["active_cell_design_id"] = (
            cell_design["id"]
        )
