import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import openai
import json
import io
from typing import Dict, List, Any
import os

# Page configuration
st.set_page_config(
    page_title="Cell Development App",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    
    .card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1e3c72;
    }
    
    .card-description {
        color: #666;
        font-size: 0.9rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        height: 80vh;
        overflow-y: auto;
    }
    
    .back-button {
        background: #6c757d;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .back-button:hover {
        background: #5a6268;
    }
    
    .performance-plot {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_material_type' not in st.session_state:
    st.session_state.selected_material_type = None
if 'selected_cathode' not in st.session_state:
    st.session_state.selected_cathode = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sample data for cathode materials
CATHODE_MATERIALS = {
    'NMC811': {
        'name': 'NMC811 (LiNi0.8Mn0.1Co0.1O2)',
        'coa_data': {
            'Property': ['Capacity', 'Voltage', 'Energy Density', 'Cycle Life', 'Thermal Stability'],
            'Value': ['200 mAh/g', '3.8V', '760 Wh/kg', '1000+ cycles', 'Good'],
            'Unit': ['mAh/g', 'V', 'Wh/kg', 'cycles', '-']
        },
        'performance_data': {
            'OCV': {'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2], 'capacity': [0, 50, 100, 150, 180, 195, 200]},
            'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]},
            'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [100, 50, 25, 15, 10, 8]}
        },
        'cycle_life': {'cycles': list(range(0, 1001, 50)), 'capacity_retention': [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60]},
        'coulombic_efficiency': {'cycles': list(range(0, 1001, 50)), 'efficiency': [99.5, 99.6, 99.7, 99.8, 99.9, 99.9, 99.8, 99.7, 99.6, 99.5, 99.4, 99.3, 99.2, 99.1, 99.0, 98.9, 98.8, 98.7, 98.6, 98.5, 98.4]}
    },
    'LCO': {
        'name': 'LCO (LiCoO2)',
        'coa_data': {
            'Property': ['Capacity', 'Voltage', 'Energy Density', 'Cycle Life', 'Thermal Stability'],
            'Value': ['140 mAh/g', '3.9V', '546 Wh/kg', '500+ cycles', 'Poor'],
            'Unit': ['mAh/g', 'V', 'Wh/kg', 'cycles', '-']
        },
        'performance_data': {
            'OCV': {'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2], 'capacity': [0, 30, 60, 90, 120, 135, 140]},
            'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]},
            'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [80, 40, 20, 12, 8, 6]}
        },
        'cycle_life': {'cycles': list(range(0, 501, 25)), 'capacity_retention': [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60]},
        'coulombic_efficiency': {'cycles': list(range(0, 501, 25)), 'efficiency': [99.0, 99.1, 99.2, 99.3, 99.4, 99.3, 99.2, 99.1, 99.0, 98.9, 98.8, 98.7, 98.6, 98.5, 98.4, 98.3, 98.2, 98.1, 98.0, 97.9, 97.8]}
    },
    'NCA': {
        'name': 'NCA (LiNi0.8Co0.15Al0.05O2)',
        'coa_data': {
            'Property': ['Capacity', 'Voltage', 'Energy Density', 'Cycle Life', 'Thermal Stability'],
            'Value': ['190 mAh/g', '3.7V', '703 Wh/kg', '800+ cycles', 'Good'],
            'Unit': ['mAh/g', 'V', 'Wh/kg', 'cycles', '-']
        },
        'performance_data': {
            'OCV': {'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2], 'capacity': [0, 45, 90, 135, 170, 185, 190]},
            'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]},
            'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [90, 45, 22, 13, 9, 7]}
        },
        'cycle_life': {'cycles': list(range(0, 801, 40)), 'capacity_retention': [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60]},
        'coulombic_efficiency': {'cycles': list(range(0, 801, 40)), 'efficiency': [99.3, 99.4, 99.5, 99.6, 99.7, 99.6, 99.5, 99.4, 99.3, 99.2, 99.1, 99.0, 98.9, 98.8, 98.7, 98.6, 98.5, 98.4, 98.3, 98.2, 98.1]}
    }
}

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🔋 Cell Development Platform</h1>
        <p>Advanced Battery Material Analysis & Design Tool</p>
    </div>
    """, unsafe_allow_html=True)

def render_home_page():
    """Render the home page with 3x3 grid of cards"""
    st.markdown("### Material Development Tools")
    
    # Create 3x3 grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔬 Material Selector", key="material_selector", use_container_width=True):
            st.session_state.current_page = 'material_selector'
            st.rerun()
        
        st.markdown("""
        <div class="card">
            <div class="card-title">🔬 Material Selector</div>
            <div class="card-description">Choose and analyze battery materials</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">⚗️ Process Optimization</div>
            <div class="card-description">Optimize manufacturing processes</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">📊 Performance Analysis</div>
            <div class="card-description">Analyze cell performance metrics</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">🔧 Cell Design</div>
            <div class="card-description">Design battery cell architecture</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">🧪 Testing Protocol</div>
            <div class="card-description">Define testing procedures</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">📈 Data Analytics</div>
            <div class="card-description">Advanced data analysis tools</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">🔄 Lifecycle Analysis</div>
            <div class="card-description">Analyze battery lifecycle</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">🌡️ Thermal Management</div>
            <div class="card-description">Thermal analysis and control</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">⚡ Fast Charging</div>
            <div class="card-description">Fast charging optimization</div>
        </div>
        """, unsafe_allow_html=True)

def render_material_selector_page():
    """Render the material selector page with cathode/anode/electrolyte/separator cards"""
    st.markdown('<button class="back-button" onclick="window.history.back()">← Back to Home</button>', unsafe_allow_html=True)
    
    st.markdown("### Select Material Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔋 Cathode Materials", key="cathode_btn", use_container_width=True):
            st.session_state.current_page = 'cathode_materials'
            st.rerun()
        
        if st.button("⚡ Anode Materials", key="anode_btn", use_container_width=True):
            st.session_state.current_page = 'anode_materials'
            st.rerun()
    
    with col2:
        if st.button("💧 Electrolyte Materials", key="electrolyte_btn", use_container_width=True):
            st.session_state.current_page = 'electrolyte_materials'
            st.rerun()
        
        if st.button("🛡️ Separator Materials", key="separator_btn", use_container_width=True):
            st.session_state.current_page = 'separator_materials'
            st.rerun()

def render_cathode_materials_page():
    """Render the cathode materials page with dropdown, table, and plots"""
    st.markdown('<button class="back-button" onclick="window.history.back()">← Back to Material Selector</button>', unsafe_allow_html=True)
    
    st.markdown("### Cathode Material Analysis")
    
    # Material selection dropdown
    selected_cathode = st.selectbox(
        "Select Cathode Material:",
        options=list(CATHODE_MATERIALS.keys()),
        key="cathode_dropdown"
    )
    
    if selected_cathode:
        material_data = CATHODE_MATERIALS[selected_cathode]
        st.session_state.selected_cathode = selected_cathode
        
        # Create two columns for table and plots
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### CoA Sheet")
            coa_df = pd.DataFrame(material_data['coa_data'])
            st.dataframe(coa_df, use_container_width=True)
        
        with col2:
            # Performance data plot selection
            plot_type = st.selectbox(
                "Select Performance Data:",
                options=['OCV', 'GITT', 'EIS'],
                key="performance_plot_type"
            )
            
            # Create performance plot
            if plot_type == 'OCV':
                fig = px.line(
                    x=material_data['performance_data']['OCV']['capacity'],
                    y=material_data['performance_data']['OCV']['voltage'],
                    title=f'{material_data["name"]} - Open Circuit Voltage',
                    labels={'x': 'Capacity (mAh/g)', 'y': 'Voltage (V)'}
                )
            elif plot_type == 'GITT':
                fig = px.line(
                    x=material_data['performance_data']['GITT']['time'],
                    y=material_data['performance_data']['GITT']['voltage'],
                    title=f'{material_data["name"]} - GITT Analysis',
                    labels={'x': 'Time (h)', 'y': 'Voltage (V)'}
                )
            else:  # EIS
                fig = px.line(
                    x=material_data['performance_data']['EIS']['frequency'],
                    y=material_data['performance_data']['EIS']['impedance'],
                    title=f'{material_data["name"]} - Electrochemical Impedance Spectroscopy',
                    labels={'x': 'Frequency (Hz)', 'y': 'Impedance (Ω)'}
                )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Cycle life and coulombic efficiency plots
            col_cycle, col_eff = st.columns(2)
            
            with col_cycle:
                cycle_fig = px.line(
                    x=material_data['cycle_life']['cycles'],
                    y=material_data['cycle_life']['capacity_retention'],
                    title='Cycle Life',
                    labels={'x': 'Cycles', 'y': 'Capacity Retention (%)'}
                )
                cycle_fig.update_layout(height=300)
                st.plotly_chart(cycle_fig, use_container_width=True)
            
            with col_eff:
                eff_fig = px.line(
                    x=material_data['coulombic_efficiency']['cycles'],
                    y=material_data['coulombic_efficiency']['efficiency'],
                    title='Coulombic Efficiency',
                    labels={'x': 'Cycles', 'y': 'Efficiency (%)'}
                )
                eff_fig.update_layout(height=300)
                st.plotly_chart(eff_fig, use_container_width=True)
        
        # Get Model Parameters button
        if st.button("📊 Get Model Parameters", key="get_params_btn", use_container_width=True):
            generate_excel_file(selected_cathode, material_data)

def generate_excel_file(material_name, material_data):
    """Generate Excel file with model parameters"""
    # Create Excel file in memory
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # OCV sheet
        ocv_df = pd.DataFrame({
            'Voltage (V)': material_data['performance_data']['OCV']['voltage'],
            'Capacity (mAh/g)': material_data['performance_data']['OCV']['capacity']
        })
        ocv_df.to_excel(writer, sheet_name='OCV', index=False)
        
        # TOCV sheet (Temperature-dependent OCV)
        ocv_voltage = material_data['performance_data']['OCV']['voltage']
        ocv_capacity = material_data['performance_data']['OCV']['capacity']
        tocv_df = pd.DataFrame({
            'Capacity (mAh/g)': ocv_capacity,
            'OCV_25C (V)': ocv_voltage,
            'OCV_45C (V)': [v + 0.05 for v in ocv_voltage],
            'OCV_60C (V)': [v + 0.1 for v in ocv_voltage]
        })
        tocv_df.to_excel(writer, sheet_name='TOCV', index=False)
        
        # Diffusion Coefficient sheet
        diff_df = pd.DataFrame({
            'SOC': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'D_li (cm²/s)': [1e-12, 1.2e-12, 1.5e-12, 1.8e-12, 2e-12, 1.8e-12, 1.5e-12, 1.2e-12, 1e-12]
        })
        diff_df.to_excel(writer, sheet_name='Diffusion_Coefficient', index=False)
        
        # Charge Transfer Kinetics sheet
        ct_df = pd.DataFrame({
            'SOC': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'k0 (A/m²)': [1e-6, 1.2e-6, 1.5e-6, 1.8e-6, 2e-6, 1.8e-6, 1.5e-6, 1.2e-6, 1e-6],
            'alpha_a': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            'alpha_c': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        })
        ct_df.to_excel(writer, sheet_name='Charge_Transfer_Kinetics', index=False)
    
    output.seek(0)
    
    # Download button
    st.download_button(
        label="📥 Download Model Parameters Excel File",
        data=output.getvalue(),
        file_name=f"{material_name}_model_parameters.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def render_chat_interface():
    """Render the chat interface"""
    st.markdown("### 🤖 AI Assistant")
    
    # Chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about battery materials..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Process the command
        response = process_chat_command(prompt)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()

def process_chat_command(prompt: str) -> str:
    """Process chat commands and control the app"""
    prompt_lower = prompt.lower()
    
    if "home" in prompt_lower or "main" in prompt_lower:
        st.session_state.current_page = 'home'
        st.rerun()
        return "Navigating to home page..."
    
    elif "material selector" in prompt_lower or "materials" in prompt_lower:
        st.session_state.current_page = 'material_selector'
        st.rerun()
        return "Opening Material Selector..."
    
    elif "cathode" in prompt_lower:
        st.session_state.current_page = 'cathode_materials'
        st.rerun()
        return "Opening Cathode Materials page..."
    
    elif "nmc811" in prompt_lower:
        st.session_state.current_page = 'cathode_materials'
        st.session_state.selected_cathode = 'NMC811'
        st.rerun()
        return "Selecting NMC811 cathode material..."
    
    elif "lco" in prompt_lower:
        st.session_state.current_page = 'cathode_materials'
        st.session_state.selected_cathode = 'LCO'
        st.rerun()
        return "Selecting LCO cathode material..."
    
    elif "nca" in prompt_lower:
        st.session_state.current_page = 'cathode_materials'
        st.session_state.selected_cathode = 'NCA'
        st.rerun()
        return "Selecting NCA cathode material..."
    
    else:
        return f"I understand you want to: {prompt}. I can help you navigate to different sections, select materials, or analyze battery data. Try commands like 'go to material selector', 'show cathode materials', or 'select NMC811'."

def main():
    """Main application function"""
    render_header()
    
    # Create main layout with 80:20 split
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Main content area (80%)
        if st.session_state.current_page == 'home':
            render_home_page()
        elif st.session_state.current_page == 'material_selector':
            render_material_selector_page()
        elif st.session_state.current_page == 'cathode_materials':
            render_cathode_materials_page()
        elif st.session_state.current_page == 'anode_materials':
            st.markdown("### Anode Materials")
            st.info("Anode materials page coming soon!")
        elif st.session_state.current_page == 'electrolyte_materials':
            st.markdown("### Electrolyte Materials")
            st.info("Electrolyte materials page coming soon!")
        elif st.session_state.current_page == 'separator_materials':
            st.markdown("### Separator Materials")
            st.info("Separator materials page coming soon!")
    
    with col2:
        # Chat interface (20%)
        render_chat_interface()

if __name__ == "__main__":
    main()
