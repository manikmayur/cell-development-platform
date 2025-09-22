"""
Workflow Tools - Regular Python functions converted from MCP tools
"""

from google.adk.tools.function_tool import FunctionTool


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


def prepare_cell_design_workflow() -> str:
    """
    This tool is always queried first when the user inquires about cell design capabilities, or
    using cell design tools is being considered by the agent, in order to provide context about the
    cell design tools available, and how to use them. 
    *DO NOT* perform any calculations by yourself Unless specifically asked to do so.
    *Always* use the tools to perform the calculations.
    *Always* be explicit in highlighting which information is verfied and which is not.
    """
    return (
        "When designing a cell, focus on the tradeoffs between performance, cost, manufacturability, and safety."
        "If trying to generate a cell design, first confirm cell dimensions and electrode formulations, always make at least 3 propositions, and render performance, cost, manufacturability, and safety tradeoffs in a radar chart."
        "Work with reasonable tradeoffs and up to 1% tolerances in design targets."
    )


def prepare_simulation_workflow() -> str:
    """
    This tool is always queried first when the user inquires about simulation capabilities, or
    using simulation tools is being considered by the agent, in order to provide context about the
    simulation tools available, and how to use them.
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


def visualization_guidelines() -> dict:
    """
    Provides guidelines for generating visualizations.
    This tool should be called every time a visualization is generated to ensure
    that the output is compatible with the environment.
    """
    return {
        "description": (
            "Visualization Guidelines:\n\n"
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


# Create FunctionTool wrappers for ADK
workflows_help_info_tool = FunctionTool(workflows_help_info)
prepare_cell_design_workflow_tool = FunctionTool(prepare_cell_design_workflow)
prepare_simulation_workflow_tool = FunctionTool(prepare_simulation_workflow)
finalize_answer_tool = FunctionTool(finalize_answer)
visualization_guidelines_tool = FunctionTool(visualization_guidelines)