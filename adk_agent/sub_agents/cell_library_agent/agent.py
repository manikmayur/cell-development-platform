import os
import logging

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


from .prompt import CELL_LIBRARY_INSTR
from adk_agent.regular_tools.database_tools import (
    store_cell_design_in_db_tool,
    search_cell_designs_in_db_tool,
    fetch_cell_design_from_db_tool,
    list_user_sessions_in_db_tool,
    delete_cell_design_from_db_tool,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"
# MODEL_NAME = "gemini-2.5-pro"

cell_library_agent = LlmAgent(
    name="cell_library_agent",
    model=LiteLlm(MODEL_NAME),
    description="Library Agent for cell design tasks",
    instruction=CELL_LIBRARY_INSTR,
    tools=[
        store_cell_design_in_db_tool,
        search_cell_designs_in_db_tool,
        fetch_cell_design_from_db_tool,
        list_user_sessions_in_db_tool,
        delete_cell_design_from_db_tool,
    ],
    output_key="cell_library_output",
)
