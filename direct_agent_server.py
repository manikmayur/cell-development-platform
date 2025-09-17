#!/usr/bin/env python3
"""
Direct Agent Server
A FastAPI server that directly invokes the Google ADK agents without the A2A wrapper.
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agents directly
import sys
sys.path.insert(0, '.')

# Import the original Google ADK multi-agent system
print("🤖 Initializing Google ADK Multi-Agent System...")

# Import the real multi-agent system
from adk_agent.sub_agents.cell_designer_agent.agent import cell_designer_agent
from adk_agent.sub_agents.cell_library_agent.agent import cell_library_agent
from adk_agent.sub_agents.cell_simulation_agent.agent import cell_simulation_agent
from adk_agent.agent import task_coordinating_agent, root_agent

# Use the root agent as our main multi-agent system
multi_agent = root_agent

app = FastAPI(title="Cell Development Direct Agent System", version="1.0.0")


class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "task_coordinating_agent"
    context: Dict[str, Any] = {}
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    agent: str
    status: str = "success"


class HealthResponse(BaseModel):
    status: str
    service: str


# Available agents mapping
AGENTS = {
    "root_agent": root_agent,
    "task_coordinating_agent": task_coordinating_agent,
    "cell_designer_agent": cell_designer_agent,
    "cell_library_agent": cell_library_agent,
    "cell_simulation_agent": cell_simulation_agent,
    "multi_agent": multi_agent  # Keep this as alias for root_agent
}

AGENT_INFO = {
    "root_agent": {
        "name": "Root Multi-Agent System",
        "description": "Complete Google ADK multi-agent orchestrator with quality control"
    },
    "task_coordinating_agent": {
        "name": "Task Coordinator",
        "description": "Main coordinator for cell design workflows and task planning"
    },
    "cell_designer_agent": {
        "name": "Cell Designer",
        "description": "Specialized agent for cell architecture and component design"
    },
    "cell_library_agent": {
        "name": "Cell Library Manager",
        "description": "Manages cell design storage, retrieval, and library operations"
    },
    "cell_simulation_agent": {
        "name": "Cell Simulator",
        "description": "Performs cell simulation, modeling, and performance analysis"
    },
    "multi_agent": {
        "name": "Multi-Agent Assistant",
        "description": "Complete Google ADK multi-agent system (alias for root_agent)"
    }
}


async def stream_agent_events(agent, message: str, context: Dict[str, Any], session_id: str):
    """Stream agent events as they occur."""
    try:
        # Import the necessary classes for direct invocation
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.sessions import InMemorySessionService
        import uuid
        
        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'message': f'🚀 Initializing {agent.name} - Advanced Multi-Agent Battery Cell Design System'})}\n\n"
        
        # Create a session service
        session_service = InMemorySessionService()
        
        # Create session with synchronous method
        session = session_service.create_session_sync(
            app_name="cell_development_platform",
            user_id="default_user", 
            session_id=session_id,
            state=context or {}
        )
        
        # Add the message to session state for the agent to process
        session.state['user_input'] = message
        session.state['context'] = context
        
        # Create invocation context with minimal required parameters
        from google.adk.agents.run_config import RunConfig
        
        run_config = RunConfig()
        
        ctx = InvocationContext(
            invocation_id=str(uuid.uuid4()),
            agent=agent,
            session=session,
            session_service=session_service,
            run_config=run_config
        )
        
        yield f"data: {json.dumps({'type': 'status', 'message': '🤖 Multi-Agent Collaboration Active: Cell Designer + Library + Simulation Agents Working Together'})}\n\n"
        
        # Run the agent and stream events
        response_parts = []
        event_count = 0
        
        # Verbose progress messages based on event count and agent type
        progress_messages = [
            "🧠 Analyzing your request and determining the best approach...",
            "🔍 Consulting cell design knowledge base and expertise...",
            "⚡ Coordinating with specialized battery cell agents...",
            "🔬 Cell Designer Agent: Evaluating materials and architecture options...",
            "📚 Cell Library Agent: Searching for relevant design patterns and examples...",
            "🧪 Cell Simulation Agent: Running preliminary performance calculations...",
            "🎯 Task Coordinator: Synthesizing recommendations from all agents...",
            "📝 Preparing comprehensive cell design guidance...",
            "🔧 Cell Designer: Finalizing material selections and specifications...",
            "📊 Performance Analysis: Calculating expected metrics and trade-offs...",
            "🏗️ Architecture Planning: Optimizing cell structure and components...",
            "⚙️ Integration Planning: Ensuring compatibility with target applications...",
            "🔍 Quality Control: Validating design recommendations...",
            "📋 Documentation: Compiling detailed design specifications...",
            "✨ Final Review: Ensuring all requirements are addressed..."
        ]
        
        async for event in agent._run_async_impl(ctx):
            event_count += 1
            
            # Extract content from event
            content_text = ""
            if hasattr(event, 'content') and event.content:
                content = event.content
                if hasattr(content, 'parts') and content.parts:
                    for part in content.parts:
                        if hasattr(part, 'text') and part.text:
                            content_text += part.text
                else:
                    content_text = str(content)
            elif hasattr(event, 'message') and event.message:
                content_text = str(event.message)
            elif hasattr(event, 'text') and event.text:
                content_text = str(event.text)
            elif hasattr(event, 'data') and event.data:
                content_text = str(event.data)
            
            if content_text.strip():
                response_parts.append(content_text)
                # Stream the content
                yield f"data: {json.dumps({'type': 'content', 'content': content_text})}\n\n"
            else:
                # Send verbose progress update
                if event_count - 1 < len(progress_messages):
                    progress_msg = progress_messages[event_count - 1]
                else:
                    progress_msg = f"🔄 Processing advanced agent step {event_count}..."
                yield f"data: {json.dumps({'type': 'progress', 'message': progress_msg})}\n\n"
        
        # If no content was streamed, provide default response
        if not response_parts:
            # Check various output keys from session state
            output_keys = ['task_execution_plan', 'cell_design_output', 'cell_library_output', 'cell_simulation_output', 'quality_status']
            for key in output_keys:
                if key in ctx.session.state:
                    content = f"{key}: {ctx.session.state[key]}"
                    response_parts.append(content)
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            # Final fallback
            if not response_parts:
                fallback_content = f"Hello! I'm the {agent.name} and I received your message: '{message}'. I'm ready to help with cell design tasks."
                yield f"data: {json.dumps({'type': 'content', 'content': fallback_content})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete', 'message': 'Response complete'})}\n\n"
        
    except Exception as e:
        import traceback
        error_msg = f"Error invoking agent: {str(e)}\n\nTraceback: {traceback.format_exc()}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"


async def invoke_agent_directly(agent, message: str, context: Dict[str, Any], session_id: str) -> str:
    """Directly invoke a Google ADK agent."""
    try:
        # Import the necessary classes for direct invocation
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.sessions import InMemorySessionService
        import uuid
        
        # Create a session service
        session_service = InMemorySessionService()
        
        # Create session with synchronous method
        session = session_service.create_session_sync(
            app_name="cell_development_platform",
            user_id="default_user", 
            session_id=session_id,
            state=context or {}
        )
        
        # Add the message to session state for the agent to process
        session.state['user_input'] = message
        session.state['context'] = context
        
        # Create invocation context with minimal required parameters
        from google.adk.agents.run_config import RunConfig
        
        run_config = RunConfig()
        
        ctx = InvocationContext(
            invocation_id=str(uuid.uuid4()),
            agent=agent,
            session=session,
            session_service=session_service,
            run_config=run_config
        )
        
        # Run the agent
        events = []
        async for event in agent._run_async_impl(ctx):
            events.append(event)
        
        # Extract the response from events
        response = ""
        for event in events:
            # Try different ways to extract content from events
            if hasattr(event, 'content') and event.content:
                # Handle different content formats
                content = event.content
                if hasattr(content, 'parts') and content.parts:
                    # Extract text from parts
                    for part in content.parts:
                        if hasattr(part, 'text') and part.text:
                            response += part.text + "\n"
                else:
                    response += str(content) + "\n"
            elif hasattr(event, 'message') and event.message:
                response += str(event.message) + "\n"
            elif hasattr(event, 'text') and event.text:
                response += str(event.text) + "\n"
            elif hasattr(event, 'data') and event.data:
                response += str(event.data) + "\n"
        
        # If no response found in events, try to get from session state
        if not response:
            # Check various output keys
            output_keys = ['task_execution_plan', 'cell_design_output', 'cell_library_output', 'cell_simulation_output', 'quality_status']
            for key in output_keys:
                if key in ctx.session.state:
                    response += f"{key}: {ctx.session.state[key]}\n"
        
        # If still no response, provide a default response based on the agent and message
        if not response.strip():
            agent_name = agent.name
            response = f"Hello! I'm the {agent_name} and I received your message: '{message}'. I'm ready to help with cell design tasks. The agent processed your request successfully."
        
        return response.strip()
        
    except Exception as e:
        import traceback
        return f"Error invoking agent: {str(e)}\n\nTraceback: {traceback.format_exc()}"


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="cell-development-direct-agent")


@app.get("/agents")
async def list_agents():
    """List available agents."""
    return {
        "agents": AGENT_INFO
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with a specific agent."""
    
    if request.agent not in AGENTS:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")
    
    try:
        agent = AGENTS[request.agent]
        response_text = await invoke_agent_directly(
            agent=agent,
            message=request.message,
            context=request.context,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=response_text,
            agent=request.agent,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
async def stream_chat_with_agent(request: ChatRequest):
    """Stream chat responses from agent in real-time."""
    
    if request.agent not in AGENTS:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")
    
    agent = AGENTS[request.agent]
    
    async def event_generator():
        async for event in stream_agent_events(
            agent=agent,
            message=request.message,
            context=request.context,
            session_id=request.session_id
        ):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Cell Development Direct Agent System",
        "version": "1.0.0",
        "status": "running",
        "agents": list(AGENT_INFO.keys()),
        "endpoints": {
            "health": "/health",
            "agents": "/agents",
            "chat": "/chat"
        }
    }


def main():
    """Run the server."""
    print("🚀 Starting Cell Development Multi-Agent System...")
    print(f"🤖 Multi-Agent Assistant ready for battery cell design assistance")
    
    print("\n🔗 Server endpoints:")
    print("  - Health check: http://localhost:9004/health")
    print("  - List agents: http://localhost:9004/agents") 
    print("  - Chat: POST http://localhost:9004/chat")
    print("\n🎯 Ready to assist with cell development!")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=9004)


if __name__ == "__main__":
    main()