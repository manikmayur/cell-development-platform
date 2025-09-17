"""
Multi-Agent Chat Interface for Cell Development Platform

This module provides an enhanced chat interface that integrates Google ADK multi-agents
with the existing Cell Development Platform. Features include:

- Google ADK multi-agent system integration
- Agent selection and routing
- Context-aware conversations
- Seamless integration with existing platform features
- Real-time agent communication

Author: Cell Development Platform Team
Version: 1.0 - Multi-agent integration
"""

import streamlit as st
import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MultiAgentChatInterface:
    """Enhanced chat interface with multi-agent support.
    
    This class provides a sophisticated chat interface that can route
    conversations to specialized agents based on user needs and context.
    
    Features:
    - Multiple specialized agents (cell designer, library, simulation)
    - Intelligent agent routing based on context
    - Fallback to traditional AI assistant
    - Agent status monitoring
    - Context preservation across agent switches
    """
    
    def __init__(self):
        """Initialize the multi-agent chat interface."""
        # Force localhost and correct port for direct agent server
        self.agent_host = "localhost"
        self.agent_port = "9004"
        self.agent_base_url = f"http://{self.agent_host}:{self.agent_port}"
        
        # Available agents and their descriptions
        self.agents = {
            "multi_agent": {
                "name": "Multi-Agent Assistant",
                "description": "Comprehensive battery cell design assistant",
                "emoji": "🤖",
                "specializes_in": ["Cell design", "Materials selection", "Performance analysis", "Workflow coordination"]
            }
        }
        
        # Check if multi-agent system is available
        self.multi_agent_available = self._check_agent_availability()
    
    def _check_agent_availability(self) -> bool:
        """Check if the multi-agent system is available."""
        try:
            response = httpx.get(f"{self.agent_base_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get current context information from session state."""
        context = {
            "current_page": st.session_state.get('current_page', 'home'),
            "selected_materials": {},
            "workflow_state": {},
            "recent_actions": []
        }
        
        # Cell design workflow context
        if 'cell_design_workflow' in st.session_state:
            context["workflow_state"] = st.session_state.cell_design_workflow
        
        # AI context
        if 'ai_context' in st.session_state:
            ai_context = st.session_state.ai_context
            context["selected_materials"] = ai_context.get('selected_materials', {})
            context["recent_actions"] = ai_context.get('recent_actions', [])
        
        return context
    
    def suggest_agent(self, user_message: str, context: Dict[str, Any]) -> str:
        """Suggest the best agent based on user message and context."""
        # Always return the multi-agent since it's our only agent
        return "multi_agent"
    
    async def stream_from_agent(self, message: str, agent_id: str, context: Dict[str, Any]):
        """Stream responses from agent in real-time."""
        if not self.multi_agent_available:
            yield "Multi-agent system is not available. Please check if the agent server is running."
            return
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": message,
                    "agent": agent_id,
                    "context": context,
                    "session_id": st.session_state.get("session_id", "default")
                }
                
                async with client.stream(
                    "POST",
                    f"{self.agent_base_url}/stream",
                    json=payload,
                    timeout=300.0  # 5 minute timeout for streaming
                ) as response:
                    if response.status_code == 200:
                        current_content = ""
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])  # Remove "data: " prefix
                                    if data["type"] == "content":
                                        current_content += data["content"]
                                        yield current_content
                                    elif data["type"] == "status":
                                        yield f"_Status: {data['message']}_"
                                    elif data["type"] == "progress":
                                        yield f"_Progress: {data['message']}_"
                                    elif data["type"] == "complete":
                                        break
                                    elif data["type"] == "error":
                                        yield f"Error: {data['content']}"
                                        break
                                except json.JSONDecodeError:
                                    continue
                    else:
                        yield f"Error: Agent returned status {response.status_code}"
                        
        except httpx.TimeoutException:
            yield "The agent stream timed out after 5 minutes. Please try a simpler question."
        except httpx.ConnectError:
            yield "Cannot connect to the agent server. Please make sure the agent server is running on port 9004."
        except Exception as e:
            yield f"Error streaming from agent: {str(e)}. Please try refreshing the status."

    async def send_to_agent(self, message: str, agent_id: str, context: Dict[str, Any]) -> str:
        """Send message to a specific agent."""
        if not self.multi_agent_available:
            return "Multi-agent system is not available. Please check if the agent server is running."
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": message,
                    "agent": agent_id,
                    "context": context,
                    "session_id": st.session_state.get("session_id", "default")
                }
                
                response = await client.post(
                    f"{self.agent_base_url}/chat",
                    json=payload,
                    timeout=120.0  # Increased timeout for complex multi-agent workflows
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No response received from agent.")
                else:
                    return f"Error: Agent returned status {response.status_code}: {response.text}"
                    
        except httpx.TimeoutException:
            return "The agent is taking longer than expected to respond. The request timed out after 2 minutes. Please try a simpler question or try again later."
        except httpx.ConnectError:
            return "Cannot connect to the agent server. Please make sure the agent server is running on port 9004."
        except Exception as e:
            return f"Error communicating with agent: {str(e)}. Please try refreshing the status or restarting the agent server."
    
    # Removed unused methods - we only have one agent now
    
    def render_enhanced_chat_interface(self):
        """Render the enhanced chat interface with multi-agent support."""
        st.markdown("### 🤖 AI Chat Assistant")
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'selected_agent' not in st.session_state:
            st.session_state.selected_agent = 'multi_agent'
        if 'streaming_active' not in st.session_state:
            st.session_state.streaming_active = False
        if 'stop_streaming' not in st.session_state:
            st.session_state.stop_streaming = False
        
        # Agent system status at top
        if st.session_state.streaming_active:
            st.info("🌊 **AI Assistant actively streaming response...** Multi-agent system working")
        elif self.multi_agent_available:
            st.success("✅ AI Assistant online - Ready for complex multi-agent queries")
        else:
            st.error("❌ AI Assistant offline")
            st.markdown("To start the AI Assistant:")
            st.code("python direct_agent_server.py")
        
        # Chat messages container
        if st.session_state.chat_history:
            with st.container(height=400):
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
        else:
            with st.container(height=400):
                st.info("👋 Welcome! Ask me anything about battery cell development. I'm your AI assistant specializing in cell design, materials, and optimization.")
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about cell development..."):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response with streaming
            with st.chat_message("assistant"):
                context = self.get_context_info()
                
                if self.multi_agent_available:
                    # Use streaming multi-agent system
                    try:
                        # Create placeholder for streaming content
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        # Stream the response with stop button
                        async def stream_response():
                            nonlocal full_response
                            st.session_state.streaming_active = True
                            st.session_state.stop_streaming = False
                            
                            try:
                                async for chunk in self.stream_from_agent(
                                    prompt,
                                    st.session_state.selected_agent,
                                    context
                                ):
                                    if st.session_state.stop_streaming:
                                        full_response += "\n\n⛔ **Streaming stopped by user**"
                                        message_placeholder.markdown(full_response)
                                        break
                                    
                                    full_response = chunk
                                    message_placeholder.markdown(full_response)
                                    
                            finally:
                                st.session_state.streaming_active = False
                                st.session_state.stop_streaming = False
                                
                            return full_response
                        
                        # Run the streaming
                        final_response = asyncio.run(stream_response())
                        
                    except Exception as e:
                        final_response = f"I apologize, but I encountered an error: {str(e)}. Please try again."
                        st.write(final_response)
                else:
                    final_response = "I'm currently offline. Please start the AI assistant server and refresh the page."
                    st.write(final_response)
                
                # Add final response to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": final_response
                })
            
            # Limit history
            if len(st.session_state.chat_history) > 50:
                st.session_state.chat_history = st.session_state.chat_history[-50:]
            
            st.rerun()
        
        # Control buttons
        if st.session_state.streaming_active:
            # Show stop button when streaming is active
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⛔ Stop Streaming", type="primary"):
                    st.session_state.stop_streaming = True
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear Chat", disabled=True):
                    pass  # Disabled while streaming
            with col3:
                if st.button("🔄 Refresh Status", disabled=True):
                    pass  # Disabled while streaming
        else:
            # Normal buttons when not streaming
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("🔄 Refresh Status"):
                    self.multi_agent_available = self._check_agent_availability()
                    st.rerun()


def render_multi_agent_chat_interface():
    """Main function to render the multi-agent chat interface."""
    chat_interface = MultiAgentChatInterface()
    chat_interface.render_enhanced_chat_interface()