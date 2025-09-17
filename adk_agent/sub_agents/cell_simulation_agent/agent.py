import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

# from adk_agent.agent import MCP_TARGET_FOLDER_PATH
from .prompt import CELL_SIMULATION_AGENT_INSTRUCTION

MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"
# MODEL_NAME = "gemini-2.5-pro"

MCP_TARGET_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../mcp_server/cell_design_mcp.py",
)

cell_simulation_agent = LlmAgent(
    name="cell_simulation_agent",
    model=LiteLlm(MODEL_NAME),
    description="Simulation Agent for cell design tasks",
    instruction=CELL_SIMULATION_AGENT_INSTRUCTION,
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
                "setup_cell_models_tool_info",
                "setup_cell_models",
                "get_cell_dcir_tool_info",
                "get_cell_dcir",
                "get_cell_power_tool_info",
                "get_cell_power",
                "check_cell_performance",
                "check_cell_performance_tool_info",
                "predict_chemistry",
                "predict_chemistry_tool_info",
                # "create_plotting_artifact",
                # "create_plotting_artifact_tool_info",
            ],
        ),
    ],
    output_key="cell_simulation_output",
)
