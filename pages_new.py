"""
Pages Module for the Cell Development Platform
Contains all page rendering functions
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
from material_data import get_default_material_data, save_coa_to_json, create_excel_export
from plotting import generate_psd_plot, create_performance_plot, create_cycle_life_plots


def render_header():
    """Render the application header"""
    st.set_page_config(
        page_title="Cell Development Platform",
        page_icon="🔋",
        layout="wide"
    )
    
    st.title("🔋 Cell Development Platform")
    st.markdown("Advanced battery cell design and analysis platform")


def render_home_page():
    """Render the home page with navigation cards"""
    st.markdown("### Welcome to the Cell Development Platform")
    st.markdown("Select a module to begin your battery cell development journey.")
    
    # Create navigation cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            border: 2px solid #1f77b4;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #f0f8ff;
            cursor: pointer;
        " onclick="window.parent.document.querySelector('[data-testid=\'baseButton-secondary\']').click()">
            <h3>🔬 Material Selector</h3>
            <p>Select and analyze cathode and anode materials</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔬 Material Selector", key="material_selector_btn", use_container_width=True):
            st.session_state.current_page = 'material_selector'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="
            border: 2px solid #2ca02c;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #f0fff0;
            cursor: pointer;
        ">
            <h3>🔧 Cell Design</h3>
            <p>Design battery cell form factor and components</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔧 Cell Design", key="cell_design_btn", use_container_width=True):
            st.session_state.current_page = 'cell_design'
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="
            border: 2px solid #ff7f0e;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #fff8f0;
            cursor: pointer;
        ">
            <h3>🤖 AI Assistant</h3>
            <p>Get help with your cell development questions</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🤖 AI Assistant", key="ai_assistant_btn", use_container_width=True):
            st.session_state.current_page = 'ai_assistant'
            st.rerun()


def render_material_selector_page():
    """Render the material selector page"""
    if st.button("← Back to Home", key="back_to_home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("### 🔬 Material Selector")
    st.markdown("Choose the type of material you want to analyze:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ Cathode Materials", key="cathode_btn", use_container_width=True):
            st.session_state.current_page = 'cathode_materials'
            st.rerun()
    
    with col2:
        if st.button("🔋 Anode Materials", key="anode_btn", use_container_width=True):
            st.session_state.current_page = 'anode_materials'
            st.rerun()


def render_cathode_materials_page():
    """Render the cathode materials page with electrode design interface"""
    if st.button("← Back to Material Selector", key="back_to_materials"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    # Import and use the electrode design function
    from electrode_design import render_cathode_electrode_design
    render_cathode_electrode_design()


def render_anode_materials_page():
    """Render the anode materials page with electrode design interface"""
    if st.button("← Back to Material Selector", key="back_to_materials_anode"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    # Import and use the electrode design function
    from electrode_design import render_anode_electrode_design
    render_anode_electrode_design()


def render_cell_design_page():
    """Render the comprehensive cell design workflow with breadcrumb navigation"""
    if st.button("← Back to Home", key="back_to_home_cell_design"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("### 🔧 Cell Design Workflow")
    st.markdown("Design your battery cell through a comprehensive step-by-step process.")
    
    # Initialize cell design manager
    if 'cell_design_manager' not in st.session_state:
        from cell_design import CellDesignManager
        st.session_state.cell_design_manager = CellDesignManager()
    
    design_manager = st.session_state.cell_design_manager
    
    # Render the workflow step
    design_manager.render_workflow_step()


def render_chat_interface():
    """Render the enhanced chat interface with context awareness"""
    st.markdown("### 🤖 AI Assistant")
    
    # Initialize AI context if not exists
    if 'ai_context' not in st.session_state:
        st.session_state.ai_context = {
            'current_page': 'home',
            'selected_materials': {},
            'recent_actions': []
        }
    
    # Display current context
    context = st.session_state.ai_context
    st.markdown("#### Current Context")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Page:** {context.get('current_page', 'home').title()}")
    with col2:
        selected_materials = [v for v in context['selected_materials'].values() if v is not None]
        st.write(f"**Selected Materials:** {', '.join(selected_materials) if selected_materials else 'None'}")
    with col3:
        recent_actions = [a for a in context['recent_actions'][-3:] if a is not None]
        st.write(f"**Recent Actions:** {', '.join(recent_actions) if recent_actions else 'None'}")
    
    # Chat interface
    st.markdown("#### Chat with AI Assistant")
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about cell development..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Simple response for now
                response = f"I understand you're asking about: {prompt}. This is a placeholder response."
                st.write(response)
                
                # Add AI response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Back button
    if st.button("← Back to Home", key="back_to_home_chat"):
        st.session_state.current_page = 'home'
        st.rerun()
