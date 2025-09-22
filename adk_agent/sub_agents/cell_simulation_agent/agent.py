import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .prompt import CELL_SIMULATION_AGENT_INSTRUCTION
from adk_agent.regular_tools.simulation_tools import (
    setup_cell_models_tool_info_tool,
    setup_cell_models_tool,
    get_cell_dcir_tool_info_tool,
    get_cell_dcir_tool,
    get_cell_power_tool_info_tool,
    get_cell_power_tool,
    check_cell_performance_tool_info_tool,
    check_cell_performance_tool,
)
from adk_agent.regular_tools.cell_design_tools import predict_cell_chemistry_tool

MODEL_NAME = "anthropic/claude-4-sonnet-20250514"
# MODEL_NAME = "openai/gpt-4o-mini"
# MODEL_NAME = "gemini-2.5-pro"

cell_simulation_agent = LlmAgent(
    name="cell_simulation_agent",
    model=LiteLlm(MODEL_NAME),
    description="Simulation Agent for cell design tasks",
    instruction=CELL_SIMULATION_AGENT_INSTRUCTION,
    tools=[
        setup_cell_models_tool_info_tool,
        setup_cell_models_tool,
        get_cell_dcir_tool_info_tool,
        get_cell_dcir_tool,
        get_cell_power_tool_info_tool,
        get_cell_power_tool,
        check_cell_performance_tool_info_tool,
        check_cell_performance_tool,
        predict_cell_chemistry_tool,
    ],
    output_key="cell_simulation_output",
)
