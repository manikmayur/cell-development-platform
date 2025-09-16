"""
Cell Development Platform - Main Application
A modular Streamlit application for battery material analysis and optimization
"""

import streamlit as st
import os
from dotenv import load_dotenv
from .pages import (
    render_header, render_home_page, render_material_selector_page,
    render_cathode_materials_page, render_anode_materials_page,
    render_cell_design_page, render_chat_interface
)
from modules.electrode_design import render_cathode_electrode_design, render_anode_electrode_design

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Page configuration
st.set_page_config(
    page_title="Cell Development Platform",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS without complex theme detection
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
    
    /* Dropdown styling for both light and dark modes */
    .stSelectbox > div > div {
        background-color: var(--background-color, #f8f9fa);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 8px;
        color: var(--text-color, #1f2937);
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color, #667eea);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div > div {
        background-color: var(--background-color, #f8f9fa);
        color: var(--text-color, #1f2937);
    }
    
    .stSelectbox > div > div > div:hover {
        background-color: var(--hover-color, #f1f5f9);
    }
    
    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        .stSelectbox > div > div {
            background-color: #1e293b;
            border-color: #334155;
            color: #f8fafc;
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
        }
        
        .stSelectbox > div > div > div {
            background-color: #1e293b;
            color: #f8fafc;
        }
        
        .stSelectbox > div > div > div:hover {
            background-color: #334155;
        }
    }
    
    /* Streamlit dark theme override */
    .stApp[data-theme="dark"] .stSelectbox > div > div {
        background-color: #1e293b;
        border-color: #334155;
        color: #f8fafc;
    }
    
    .stApp[data-theme="dark"] .stSelectbox > div > div:focus-within {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
    }
    
    /* CSS Variables for theme support */
    :root {
        --background-color: #ffffff;
        --text-color: #1f2937;
        --text-color-secondary: #6b7280;
        --border-color: #e5e7eb;
        --primary-color: #667eea;
        --success-color: #10b981;
        --hover-color: #f1f5f9;
    }
    
    /* Dark theme variables */
    .stApp[data-theme="dark"] {
        --background-color: #0f172a;
        --text-color: #f8fafc;
        --text-color-secondary: #94a3b8;
        --border-color: #334155;
        --primary-color: #8b5cf6;
        --success-color: #10b981;
        --hover-color: #1e293b;
    }
    
    /* Dark mode media query fallback */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0f172a;
            --text-color: #f8fafc;
            --text-color-secondary: #94a3b8;
            --border-color: #334155;
            --primary-color: #8b5cf6;
            --success-color: #10b981;
            --hover-color: #1e293b;
        }
    }
    
    /* Simple button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    
    /* Dark theme button styling */
    .stApp[data-theme="dark"] .stButton > button {
        background: linear-gradient(90deg, #8b5cf6 0%, #a855f7 100%) !important;
        color: white !important;
    }
    
    /* Fixed height chat container with scrolling */
    #chat-messages {
        height: 400px !important;
        overflow-y: auto !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 16px !important;
        background: #ffffff !important;
        margin-bottom: 16px !important;
        scroll-behavior: smooth !important;
    }
    
    .stApp[data-theme="dark"] #chat-messages {
        background: #1e293b !important;
        border-color: #334155 !important;
    }
    
    /* Chat message styling */
    .stChatMessage {
        margin-bottom: 16px !important;
    }
    
    /* Ensure chat messages are properly displayed */
    .stChatMessage > div {
        background: transparent !important;
    }
    
    /* Custom scrollbar for chat container */
    #chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    #chat-messages::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    #chat-messages::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    #chat-messages::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    .stApp[data-theme="dark"] #chat-messages::-webkit-scrollbar-track {
        background: #374151;
    }
    
    .stApp[data-theme="dark"] #chat-messages::-webkit-scrollbar-thumb {
        background: #6b7280;
    }
    
    .stApp[data-theme="dark"] #chat-messages::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }
    
    .stApp[data-theme="dark"] .stSelectbox > div > div > div {
        background-color: #1e293b;
        color: #f8fafc;
    }
    
    .stApp[data-theme="dark"] .stSelectbox > div > div > div:hover {
        background-color: #334155;
    }
    
    /* Text input styling for both light and dark modes */
    .stTextInput > div > div > input {
        background-color: var(--background-color, #f8f9fa);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 8px;
        color: var(--text-color, #1f2937);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color, #667eea);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        background-color: var(--background-color, #f8f9fa);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 8px;
        color: var(--text-color, #1f2937);
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color, #667eea);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background-color: var(--primary-color, #667eea);
    }
    
    .stSlider > div > div > div > div > div {
        background-color: var(--primary-color, #667eea);
    }
    
    /* Checkbox styling */
    .stCheckbox > label > div {
        background-color: var(--background-color, #f8f9fa);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 4px;
    }
    
    .stCheckbox > label > div[data-checked="true"] {
        background-color: var(--primary-color, #667eea);
        border-color: var(--primary-color, #667eea);
    }
    
    /* Dark mode overrides for all form elements */
    @media (prefers-color-scheme: dark) {
        .stTextInput > div > div > input {
            background-color: #1e293b;
            border-color: #334155;
            color: #f8fafc;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
        }
        
        .stNumberInput > div > div > input {
            background-color: #1e293b;
            border-color: #334155;
            color: #f8fafc;
        }
        
        .stNumberInput > div > div > input:focus {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
        }
        
        .stSlider > div > div > div > div {
            background-color: #8b5cf6;
        }
        
        .stSlider > div > div > div > div > div {
            background-color: #8b5cf6;
        }
        
        .stCheckbox > label > div {
            background-color: #1e293b;
            border-color: #334155;
        }
        
        .stCheckbox > label > div[data-checked="true"] {
            background-color: #8b5cf6;
            border-color: #8b5cf6;
        }
    }
    
    /* Streamlit dark theme overrides for all form elements */
    .stApp[data-theme="dark"] .stTextInput > div > div > input {
        background-color: #1e293b;
        border-color: #334155;
        color: #f8fafc;
    }
    
    .stApp[data-theme="dark"] .stTextInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
    }
    
    .stApp[data-theme="dark"] .stNumberInput > div > div > input {
        background-color: #1e293b;
        border-color: #334155;
        color: #f8fafc;
    }
    
    .stApp[data-theme="dark"] .stNumberInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
    }
    
    .stApp[data-theme="dark"] .stSlider > div > div > div > div {
        background-color: #8b5cf6;
    }
    
    .stApp[data-theme="dark"] .stSlider > div > div > div > div > div {
        background-color: #8b5cf6;
    }
    
    .stApp[data-theme="dark"] .stCheckbox > label > div {
        background-color: #1e293b;
        border-color: #334155;
    }
    
    .stApp[data-theme="dark"] .stCheckbox > label > div[data-checked="true"] {
        background-color: #8b5cf6;
        border-color: #8b5cf6;
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
            from .pages import render_cathode_materials_page_new
            render_cathode_materials_page_new()
        elif st.session_state.current_page == 'anode_materials':
            from .pages import render_anode_materials_page_new
            render_anode_materials_page_new()
        elif st.session_state.current_page == 'cathode_electrode_design':
            render_cathode_electrode_design()
        elif st.session_state.current_page == 'anode_electrode_design':
            render_anode_electrode_design()
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
        elif st.session_state.current_page == 'ocv_curves':
            from pages import render_ocv_curves_page
            render_ocv_curves_page()
        elif st.session_state.current_page == 'coa_management':
            from pages import render_coa_management_page
            render_coa_management_page()
    
    with col2:
        # AI Assistant sidebar
        render_chat_interface()

if __name__ == "__main__":
    main()
