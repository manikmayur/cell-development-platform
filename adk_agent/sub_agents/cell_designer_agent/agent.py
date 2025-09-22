import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import agent_tool


from adk_agent.sub_agents.cell_library_agent.agent import (
    cell_library_agent,
)
from .prompt import CELL_DESIGNER_AGENT_INSTRUCTION
from .tools import _escalate_if_needed
from adk_agent.regular_tools.cell_design_tools import (
    get_cell_design_tool_info_tool,
    get_cell_design_tool,
    get_valid_cell_design_aliases_tool,
    estimate_bill_of_materials_tool,
)

# Example using a local SQLite file:
# db_url = "sqlite:///./cell_design_agent_db.sqlite"
# session_service = DatabaseSessionService(db_url=db_url)
# MODEL_NAME = "gemini-2.5-pro"
MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"

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
        get_cell_design_tool_info_tool,
        get_cell_design_tool,
        get_valid_cell_design_aliases_tool,
        estimate_bill_of_materials_tool,
    ],
    # after_agent_callback=_update_internal_state,
    after_agent_callback=_escalate_if_needed,
    output_key="cell_design_output",
)
