import os
from typing import AsyncGenerator
import warnings
import logging

from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.models.lite_llm import LiteLlm
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import agent_tool
from typing import AsyncGenerator

from .sub_agents.cell_designer_agent.agent import cell_designer_agent
from .sub_agents.cell_library_agent.agent import cell_library_agent
from .sub_agents.cell_simulation_agent.agent import cell_simulation_agent
from .regular_tools.workflow_tools import (
    workflows_help_info_tool,
    prepare_cell_design_workflow_tool,
    prepare_simulation_workflow_tool,
)

from starlette.responses import JSONResponse

from .prompts import (
    CELL_DESIGN_COORDINATING_AGENT_INSTRUCTION,
    QUALITY_CHECKER_INSTRUCTION,
    CRITIQUE_AGENT_INSTRUCTION,
)

from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# MODEL_NAME = "gemini-2.5-pro"
MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"

cell_design_library_tool = agent_tool.AgentTool(
    agent=cell_library_agent, 
    skip_summarization=True
)

# cell_simulation_coordinating_agent = LlmAgent(
#     name="cell_simulation_coordinating_agent",
#     model=LiteLlm(MODEL_NAME),
#     description="Coordinating Agent for cell simulation tasks",
#     instruction=CELL_SIMULATION_COORDINATING_AGENT_INSTRUCTION,
#     tools=[
#         MCPToolset(
#             connection_params=StdioConnectionParams(
#                 server_params=StdioServerParameters(
#                     command="mcp",
#                     args=[
#                         "run",
#                         os.path.abspath(MCP_TARGET_FOLDER_PATH),
#                     ],
#                 ),
#             ),
#             tool_filter=["workflows_help_info", "prepare_cell_simulation_workflow"],
#         ),
#         # cell_design_library_tool,
#     ],
#     sub_agents=[
#         cell_simulation_agent,
#         # cell_design_library_agent,
#     ],
#     output_key="cell_simulation_execution_plan",
# )

task_coordinating_agent = LlmAgent(
    name="task_coordinating_agent",
    model=LiteLlm(MODEL_NAME),
    description="Coordinating Agent for cell design tasks",
    instruction=CELL_DESIGN_COORDINATING_AGENT_INSTRUCTION,
    tools=[
        workflows_help_info_tool,
        prepare_cell_design_workflow_tool,
        prepare_simulation_workflow_tool,
    ],
    sub_agents=[
        cell_designer_agent,
        cell_library_agent,
        cell_simulation_agent,
    ],
    output_key="task_execution_plan",
    disallow_transfer_to_peers=True,  # Reduce unnecessary transfers
    # after_agent_callback=filter_agent_output  # Filter display based on config
)
critique_agent = LlmAgent(
    name="cell_design_critique_agent",
    model=LiteLlm(MODEL_NAME),
    description="A2A Agent for cell design tasks - Critique Agent",
    instruction=CRITIQUE_AGENT_INSTRUCTION,
)

critique_tool = agent_tool.AgentTool(
    agent=critique_agent, 
    skip_summarization=False
)

# Agent to check if the code meets quality standards
response_quality_checker = LlmAgent(
    model=LiteLlm(MODEL_NAME),
    name="QualityChecker",
    instruction=QUALITY_CHECKER_INSTRUCTION,
    tools=[critique_tool],
    output_key="quality_status",

)


# Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("quality_status", "fail")
        should_stop = status == "pass"
        status = ctx.session.state.get("task_execution_plan", "incomplete")
        if any(x in status.lower() for x in ["?", "please", "what", "should i"]):
            ctx.session.state["task_execution_plan"] = status + "incomplete"
            should_stop = True
        status = ctx.session.state.get("cell_designer_output", "incomplete")
        if any(x in status.lower() for x in ["?", "please", "what", "should i"]):
            ctx.session.state["cell_designer_output"] = status + "incomplete"
            should_stop = True
        # status = ctx.session.state.get("cell_simulation_execution_plan", "incomplete")
        # if any(x in status.lower() for x in ["?", "please", "what", "should i"]):
        #     ctx.session.state["cell_simulation_execution_plan"] = status + "incomplete"
        #     should_stop = True
        if "?" in ctx.session.state.get("cell_library_output", "incomplete"):
            should_stop = True
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


root_agent = LoopAgent(
    name="cell_design_agent_sequence",
    max_iterations=3,
    sub_agents=[
        task_coordinating_agent,
        CheckStatusAndEscalate(name="StopChecker"),
        response_quality_checker,
        CheckStatusAndEscalate(name="StopChecker"),
    ],
)

a2a_app = to_a2a(root_agent, host="host.docker.internal", port=9003)

# Add health endpoint for Kubernetes health checks
async def health_check(request):
    """Health check endpoint for Kubernetes liveness and readiness probes"""
    return JSONResponse({"status": "healthy", "service": "cell-design-agent"})

# Add the health route to the Starlette app
a2a_app.add_route("/health", health_check, methods=["GET"])
