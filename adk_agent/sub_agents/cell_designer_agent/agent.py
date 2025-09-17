import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)
from google.adk.tools import agent_tool


from adk_agent.sub_agents.cell_library_agent.agent import (
    cell_library_agent,
)
from .prompt import CELL_DESIGNER_AGENT_INSTRUCTION
from .tools import _escalate_if_needed

# Example using a local SQLite file:
# db_url = "sqlite:///./cell_design_agent_db.sqlite"
# session_service = DatabaseSessionService(db_url=db_url)
# MODEL_NAME = "gemini-2.5-pro"
MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"
MCP_TARGET_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../mcp_server/cell_design_mcp.py",
)

cell_library_tool = agent_tool.AgentTool(
    agent=cell_library_agent, 
    skip_summarization=True
)  # Wrap the agent

cell_designer_agent = LlmAgent(
    name="cell_designer_agent",
    model=LiteLlm(MODEL_NAME),
    description="An agent to produce cell designs.",
    instruction=CELL_DESIGNER_AGENT_INSTRUCTION,
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
            # Optional: Filter which tools from the MCP server are exposed
            tool_filter=[
                "get_cell_design_tool_info",
                "get_cell_design",
                "get_valid_cell_design_aliases",
                "estimate_bill_of_materials",
            ],
        ),
        # cell_design_library_tool,
    ],
    # after_agent_callback=_update_internal_state,
    after_agent_callback=_escalate_if_needed,
    output_key="cell_design_output",
)
