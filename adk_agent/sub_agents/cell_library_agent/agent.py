import os
import logging

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

from .prompt import CELL_LIBRARY_INSTR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"
# MODEL_NAME = "gemini-2.5-pro"

MCP_TARGET_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../mcp_server/cell_design_mcp.py",
)

# cell_library_agent = LlmAgent(
#     name="cell_library_agent",
#     model=LiteLlm(MODEL_NAME),
#     description="A2A Agent for cell design tasks - Cell library Agent",
#     instruction=CELL_LIBRARY_INSTR,
#     tools=[
#         # store_cell_design,
#         show_stored_cell_designs,
#         set_active_cell_design,
#         get_active_cell_design,
#         find_cell_design_by_id,
#         find_cell_design_by_context,
#     ],
#     output_key="cell_library_state",
#     # before_agent_callback=_set_initial_states,
# )

MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "gemini-2.5-pro"

MCP_TARGET_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../mcp_server/cell_design_mcp.py",
)

cell_library_agent = LlmAgent(
    name="cell_library_agent",
    model=LiteLlm(MODEL_NAME),
    description="Library Agent for cell design tasks",
    instruction=CELL_LIBRARY_INSTR,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="mcp",
                    args=[
                        "run",
                        os.path.abspath(MCP_TARGET_FOLDER_PATH),
                    ],
                ),
                timeout=300,
            ),
            tool_filter=[
                "store_cell_design_in_db",
                "search_cell_designs_in_db",
                "fetch_cell_design_from_db",
                "get_cell_design_inventory_from_db",
                "update_cell_design_in_db",
                "clear_all_cell_designs",
            ],
        ),
    ],
    output_key="cell_library_output",
)
