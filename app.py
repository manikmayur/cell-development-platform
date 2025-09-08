"""
Cell Development Platform - Main Application
A modular Streamlit application for battery material analysis and optimization
"""

import streamlit as st
import os
from pages import (
    render_header, render_home_page, render_material_selector_page,
    render_cathode_materials_page, render_anode_materials_page,
    render_cell_design_page, render_chat_interface
)

# Page configuration
st.set_page_config(
    page_title="Cell Development Platform",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: bold;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Main content area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Render current page
        if st.session_state.current_page == 'home':
            render_home_page()
        elif st.session_state.current_page == 'material_selector':
            render_material_selector_page()
        elif st.session_state.current_page == 'cathode_materials':
            render_cathode_materials_page()
        elif st.session_state.current_page == 'anode_materials':
            render_anode_materials_page()
        elif st.session_state.current_page == 'cell_design':
            render_cell_design_page()
        elif st.session_state.current_page == 'electrolyte_materials':
            st.markdown("### Electrolyte Materials")
            st.info("Electrolyte materials page coming soon!")
        elif st.session_state.current_page == 'separator_materials':
            st.markdown("### Separator Materials")
            st.info("Separator materials page coming soon!")
        elif st.session_state.current_page == 'process_optimization':
            st.markdown("### Process Optimization")
            st.info("Process optimization page coming soon!")
        elif st.session_state.current_page == 'performance_analysis':
            st.markdown("### Performance Analysis")
            st.info("Performance analysis page coming soon!")
        elif st.session_state.current_page == 'testing_protocol':
            st.markdown("### Testing Protocol")
            st.info("Testing protocol page coming soon!")
        elif st.session_state.current_page == 'data_analytics':
            st.markdown("### Data Analytics")
            st.info("Data analytics page coming soon!")
        elif st.session_state.current_page == 'lifecycle_analysis':
            st.markdown("### Lifecycle Analysis")
            st.info("Lifecycle analysis page coming soon!")
        elif st.session_state.current_page == 'thermal_management':
            st.markdown("### Thermal Management")
            st.info("Thermal management page coming soon!")
        elif st.session_state.current_page == 'fast_charging':
            st.markdown("### Fast Charging")
            st.info("Fast charging page coming soon!")
    
    with col2:
        # AI Assistant sidebar
        render_chat_interface()

if __name__ == "__main__":
    main()
