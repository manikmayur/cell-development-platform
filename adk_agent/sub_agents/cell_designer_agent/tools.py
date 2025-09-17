from google.adk.events import Event, EventActions

def _escalate_if_needed(callback_context):
    """
    Escalates the cell design if needed.
    """
    should_stop = False
    
    # Check task execution plan
    status = callback_context.session.state.get("task_execution_plan", "incomplete")
    if any(x in status.lower() for x in ["?", "please", "what", "should i"]):
        callback_context.session.state["task_execution_plan"] = status + "incomplete"
        should_stop = True
    
    # Check cell designer output
    status = callback_context.session.state.get("cell_designer_output", "incomplete")
    if any(x in status.lower() for x in ["?", "please", "what", "should i"]):
        callback_context.session.state["cell_designer_output"] = status + "incomplete"
        should_stop = True
    
    # Check cell library output
    if "?" in callback_context.session.state.get("cell_library_output", "incomplete"):
        should_stop = True
    
    yield Event(author=callback_context.agent.name, actions=EventActions(escalate=should_stop))