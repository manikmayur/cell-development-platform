"""
AI Assistant Module for Cell Development Platform

This module provides an intelligent, context-aware chat interface for the
battery cell development platform. Features include:

- OpenAI GPT-4 powered conversational AI
- Context awareness of current design workflow state
- Material-specific knowledge and guidance
- Natural language navigation commands
- Real-time chat with scrollable message history
- Integration with all platform modules

The AI assistant can help users:
- Navigate the application
- Understand material properties and selections
- Get design recommendations
- Troubleshoot issues
- Learn about battery cell development concepts

Author: Cell Development Platform Team
Version: 2.0 - Enhanced context awareness
"""

# Core libraries
import streamlit as st
import openai
import os
from typing import List, Dict, Any
import json

# Environment management
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class CellDevelopmentAI:
    """Context-aware AI assistant for battery cell development platform.
    
    This class provides intelligent conversational assistance for battery cell
    development workflows. It maintains awareness of the current design state
    and provides contextually relevant guidance.
    
    Features:
    - GPT-4 powered natural language processing
    - Context awareness of current workflow step and selections
    - Material-specific knowledge base
    - Design recommendations and best practices
    - Natural language navigation commands
    - Error handling and graceful degradation
    
    Attributes:
        client: OpenAI API client for GPT-4 interactions
        system_prompt: Expert system prompt for battery cell development
    
    Methods:
        get_context_info(): Extract current workflow context
        generate_response(): Generate contextual AI responses
        render_chat_interface(): Render the chat UI with scrolling
    """
    
    def __init__(self):
        # Check if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("⚠️ OpenAI API key not found. Please create a .env file with your OPENAI_API_KEY. See ENV_SETUP.md for instructions.")
            self.client = None
        else:
            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=api_key)
        
        # System prompt for cell development context
        self.system_prompt = """You are an expert AI assistant specialized in battery cell development and materials science. 
        
        Your expertise includes:
        - Battery cell design and optimization
        - Electrode materials (cathode and anode)
        - Electrolyte and separator selection
        - Cell form factors (cylindrical, pouch, prismatic)
        - Safety features and thermal management
        - Performance simulation and analysis
        - Material properties and characterization
        
        You should provide:
        - Technical insights and recommendations
        - Material selection guidance
        - Design optimization suggestions
        - Safety considerations
        - Performance analysis
        - Clear explanations of complex concepts
        
        Always be helpful, accurate, and provide actionable advice for battery cell development."""
    
    def get_context_info(self) -> str:
        """Get current context information from session state"""
        context_parts = []
        
        # Current page context
        current_page = st.session_state.get('current_page', 'home')
        context_parts.append(f"Current page: {current_page.replace('_', ' ').title()}")
        
        # Cell design workflow context
        if 'cell_design_workflow' in st.session_state:
            workflow = st.session_state.cell_design_workflow
            if workflow.get('form_factor'):
                context_parts.append(f"Selected form factor: {workflow['form_factor'].title()}")
            if workflow.get('casing_material'):
                context_parts.append(f"Selected casing material: {workflow['casing_material']}")
            if workflow.get('cathode_material'):
                context_parts.append(f"Selected cathode material: {workflow['cathode_material']}")
            if workflow.get('anode_material'):
                context_parts.append(f"Selected anode material: {workflow['anode_material']}")
            if workflow.get('electrolyte'):
                context_parts.append(f"Selected electrolyte: {workflow['electrolyte']}")
            if workflow.get('separator'):
                context_parts.append(f"Selected separator: {workflow['separator']}")
        
        # Selected materials context
        if 'ai_context' in st.session_state:
            ai_context = st.session_state.ai_context
            selected_materials = [v for v in ai_context.get('selected_materials', {}).values() if v is not None]
            if selected_materials:
                context_parts.append(f"Selected materials: {', '.join(selected_materials)}")
        
        return " | ".join(context_parts) if context_parts else "No specific context available"
    
    def generate_response(self, user_message: str, chat_history: List[Dict[str, str]]) -> str:
        """Generate AI response using OpenAI API"""
        if self.client is None:
            return "I'm sorry, but I cannot respond without a valid OpenAI API key. Please check your .env file configuration."
        
        try:
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add context information
            context_info = self.get_context_info()
            if context_info != "No specific context available":
                messages.append({
                    "role": "system", 
                    "content": f"Current context: {context_info}"
                })
            
            # Add recent chat history (last 10 messages to stay within token limits)
            recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
            for message in recent_history:
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please check your OpenAI API key and try again."
    
    def render_chat_interface(self):
        """Render the chat interface with fixed height and scrolling"""
        st.markdown("### Chat With Protos")
        
        # Initialize chat history and context
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'ai_context' not in st.session_state:
            st.session_state.ai_context = {
                'current_page': 'home',
                'selected_materials': {},
                'recent_actions': []
            }
        
        # Display current context
        with st.expander("📊 Current Context", expanded=False):
            context = st.session_state.ai_context
            st.write(f"**Current Page:** {context['current_page'].replace('_', ' ').title()}")
            if context['selected_materials']:
                selected = [v for v in context['selected_materials'].values() if v is not None]
                if selected:
                    st.write(f"**Selected Materials:** {', '.join(selected)}")
            
            # Show cell design workflow context
            if 'cell_design_workflow' in st.session_state:
                workflow = st.session_state.cell_design_workflow
                workflow_info = []
                if workflow.get('form_factor'):
                    workflow_info.append(f"Form Factor: {workflow['form_factor'].title()}")
                if workflow.get('casing_material'):
                    workflow_info.append(f"Casing: {workflow['casing_material']}")
                if workflow.get('cathode_material'):
                    workflow_info.append(f"Cathode: {workflow['cathode_material']}")
                if workflow.get('anode_material'):
                    workflow_info.append(f"Anode: {workflow['anode_material']}")
                
                if workflow_info:
                    st.write(f"**Design Workflow:** {' | '.join(workflow_info)}")
        
        # Create chat messages container with proper scrolling
        if st.session_state.chat_history:
            # Display chat messages with height constraint
            with st.container(height=400):
                # Display all messages in chronological order
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
        else:
            # Show welcome message when no chat history
            with st.container(height=400):
                st.info("👋 Welcome! Ask me anything about battery cell development...")
        
        # Chat input at the bottom
        if prompt := st.chat_input("Ask me anything about cell development..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Initialize AI assistant
                    if 'ai_assistant' not in st.session_state:
                        st.session_state.ai_assistant = CellDevelopmentAI()
                    
                    ai_assistant = st.session_state.ai_assistant
                    response = ai_assistant.generate_response(prompt, st.session_state.chat_history)
                    st.write(response)
                    
                    # Add AI response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Limit chat history to prevent memory issues (keep last 50 messages)
            if len(st.session_state.chat_history) > 50:
                st.session_state.chat_history = st.session_state.chat_history[-50:]
            
            st.rerun()
        
        # Clear chat button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Back button
        with col2:
            if st.button("← Back to Home", key="back_to_home_chat"):
                st.session_state.current_page = 'home'
                st.rerun()


def render_chat_interface():
    """Main function to render the chat interface"""
    ai_assistant = CellDevelopmentAI()
    ai_assistant.render_chat_interface()