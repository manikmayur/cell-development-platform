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
from modules.material_data import get_default_material_data
from modules.ocv_curves import OCVCurveGenerator
from modules.coa_performance import render_anode_page, render_cathode_page
from modules.coa_manager import render_coa_management_page


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
    """Render the home page with 3x3 grid of buttons"""
    st.markdown("### Material Development Tools")
    
    # Create 3x3 grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Material Selector button
        if st.button("🔬 Material Selector\n\nChoose and analyze battery materials", key="material_selector", use_container_width=True, help="Click to open Material Selector"):
            st.session_state.current_page = 'material_selector'
            st.rerun()
        
        # Process Optimization button
        if st.button("⚗️ Process Optimization\n\nOptimize manufacturing processes", key="process_optimization", use_container_width=True, help="Click to open Process Optimization"):
            st.session_state.current_page = 'process_optimization'
            st.rerun()
        
        # Performance Analysis button
        if st.button("📊 Performance Analysis\n\nAnalyze cell performance metrics", key="performance_analysis", use_container_width=True, help="Click to open Performance Analysis"):
            st.session_state.current_page = 'performance_analysis'
            st.rerun()
    
    with col2:
        # Cell Design button
        if st.button("🔧 Cell Design\n\nDesign battery cell architecture", key="cell_design", use_container_width=True, help="Click to open Cell Design"):
            st.session_state.current_page = 'cell_design'
            st.rerun()
        
        # Testing Protocol button
        if st.button("🧪 Testing Protocol\n\nDefine testing procedures", key="testing_protocol", use_container_width=True, help="Click to open Testing Protocol"):
            st.session_state.current_page = 'testing_protocol'
            st.rerun()
        
        # Data Analytics button
        if st.button("📈 Data Analytics\n\nAdvanced data analysis tools", key="data_analytics", use_container_width=True, help="Click to open Data Analytics"):
            st.session_state.current_page = 'data_analytics'
            st.rerun()
        
        # OCV Curves button
        if st.button("🔋 OCV Curves\n\nOpen circuit voltage analysis", key="ocv_curves", use_container_width=True, help="Click to open OCV Curves"):
            st.session_state.current_page = 'ocv_curves'
            st.rerun()
        
        # CoA Management button
        if st.button("📋 CoA Management\n\nCertificate of Analysis management", key="coa_management", use_container_width=True, help="Click to open CoA Management"):
            st.session_state.current_page = 'coa_management'
            st.rerun()
    
    with col3:
        # Lifecycle Analysis button
        if st.button("🔄 Lifecycle Analysis\n\nAnalyze battery lifecycle", key="lifecycle_analysis", use_container_width=True, help="Click to open Lifecycle Analysis"):
            st.session_state.current_page = 'lifecycle_analysis'
            st.rerun()
        
        # Thermal Management button
        if st.button("🌡️ Thermal Management\n\nThermal analysis and control", key="thermal_management", use_container_width=True, help="Click to open Thermal Management"):
            st.session_state.current_page = 'thermal_management'
            st.rerun()
        
        # Fast Charging button
        if st.button("⚡ Fast Charging\n\nFast charging optimization", key="fast_charging", use_container_width=True, help="Click to open Fast Charging"):
            st.session_state.current_page = 'fast_charging'
            st.rerun()


def render_material_selector_page():
    """Render the material selector page with cathode/anode/electrolyte/separator buttons"""
    if st.button("← Back to Home", key="back_to_home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("### Select Material Type")
    
    # Create 2x2 grid for material types
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
    """Render the cathode materials page with CoA data editing"""
    if st.button("← Back to Material Selector", key="back_to_materials"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    st.markdown("### ⚡ Cathode Materials Analysis")
    
    # Material selection
    # Check if material was passed from cell design workflow
    if 'selected_cathode' in st.session_state:
        default_index = ['NMC811', 'LCO', 'NCA'].index(st.session_state.selected_cathode) if st.session_state.selected_cathode in ['NMC811', 'LCO', 'NCA'] else 0
    else:
        default_index = 0
    
    selected_cathode = st.selectbox(
        "Select Cathode Material:",
        options=['NMC811', 'LCO', 'NCA', 'LFP', 'NMC532'],
        index=default_index,
        key="cathode_selector"
    )
    
    # Initialize session state for selected material
    coa_key = f"coa_data_{selected_cathode}"
    if coa_key not in st.session_state:
        st.session_state[coa_key] = get_default_material_data(selected_cathode)['coa_data']
    
    material_data = get_default_material_data(selected_cathode)
    
    # Display material info
    st.markdown(f"**Selected Material:** {material_data['name']}")
    
    # CoA Data Editing Section
    st.markdown("#### CoA Data Editor")
    
    # Prepare data for the editable table
    coa_data = st.session_state[coa_key]
    editable_data = {
        'Category': [
            'Particle Size', 'Particle Size', 'Particle Size', 'Particle Size', 'Particle Size',
            'Surface & Density', 'Surface & Density', 'Surface & Density', 'Surface & Density',
            'Electrochemical', 'Electrochemical', 'Electrochemical', 'Electrochemical',
            'Chemical Composition', 'Chemical Composition', 'Chemical Composition', 'Chemical Composition'
        ],
        'Property': [
            'D-min (μm)', 'D10 (μm)', 'D50 (μm)', 'D90 (μm)', 'D-max (μm)',
            'BET Surface Area (m²/g)', 'Tap Density (g/cm³)', 'Bulk Density (g/cm³)', 'True Density (g/cm³)',
            'Specific Capacity (mAh/g)', 'Nominal Voltage (V)', 'Energy Density (Wh/kg)', 'Cycle Life (cycles)',
            'Moisture Content (%)', 'Total Impurities (ppm)', 'pH Value', 'Crystallinity (%)'
        ],
        'Value': [
            coa_data.get('D_min', 0.5), coa_data.get('D10', 2.1), coa_data.get('D50', 8.5),
            coa_data.get('D90', 18.2), coa_data.get('D_max', 45.0),
            coa_data.get('BET', 0.8), coa_data.get('tap_density', 2.4),
            coa_data.get('bulk_density', 1.8), coa_data.get('true_density', 4.7),
            coa_data.get('capacity', 200), coa_data.get('voltage', 3.8),
            coa_data.get('energy_density', 760), coa_data.get('cycle_life', 1000),
            coa_data.get('moisture', 0.02), coa_data.get('impurities', 50),
            coa_data.get('pH', 11.5), coa_data.get('crystallinity', 98.5)
        ]
    }
    
    edited_df = st.data_editor(
        pd.DataFrame(editable_data),
        column_config={
            "Category": st.column_config.TextColumn("Category", disabled=True),
            "Property": st.column_config.TextColumn("Property", disabled=True),
            "Value": st.column_config.NumberColumn("Value", step=0.01, format="%.3f")
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )
    
    # Extract values from edited table
    values = edited_df['Value'].tolist()
    d_min, d10, d50, d90, d_max = values[0:5]
    bet_surface, tap_density, bulk_density, true_density = values[5:9]
    capacity, voltage, energy_density, cycle_life = values[9:13]
    moisture, impurities, ph_value, crystallinity = values[13:17]
    
    # Update button
    if st.button("📊 Update CoA Data", key=f"update_coa_{selected_cathode}", use_container_width=True):
        # Update session state with new values
        updated_coa_data = {
            'D_min': d_min, 'D10': d10, 'D50': d50, 'D90': d90, 'D_max': d_max,
            'BET': bet_surface, 'tap_density': tap_density, 'bulk_density': bulk_density, 'true_density': true_density,
            'capacity': capacity, 'voltage': voltage, 'energy_density': energy_density, 'cycle_life': cycle_life,
            'moisture': moisture, 'impurities': impurities, 'pH': ph_value, 'crystallinity': crystallinity
        }
        st.session_state[coa_key] = updated_coa_data
        st.success(f"✅ CoA data updated successfully for {selected_cathode}")
        st.rerun()
    
    # PSD Plot Section
    st.markdown("#### Particle Size Distribution")
    
    # Create PSD plot
    try:
        from plotting import generate_psd_plot
        generate_psd_plot(st.session_state[coa_key], 'Both', selected_cathode)
    except Exception as e:
        st.error(f"Error generating PSD plot: {str(e)}")
        st.info("Make sure scipy is installed: pip install scipy")
    
    # Performance plots
    st.markdown("#### Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # OCV plot
        soc = np.linspace(0, 100, 100)
        voltage = 3.7 - 0.5 * (soc/100) + 0.2 * np.sin(2 * np.pi * soc/100)
        
        fig = px.line(x=soc, y=voltage, title="OCV vs SOC")
        fig.update_layout(xaxis_title="State of Charge (%)", yaxis_title="Voltage (V)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cycle life plot
        cycles = np.linspace(0, 1000, 100)
        capacity_retention = 100 * np.exp(-cycles/2000)
        
        fig = px.line(x=cycles, y=capacity_retention, title="Cycle Life")
        fig.update_layout(xaxis_title="Cycle Number", yaxis_title="Capacity Retention (%)")
        st.plotly_chart(fig, use_container_width=True)


def render_anode_materials_page():
    """Render the anode materials page with CoA data editing"""
    if st.button("← Back to Material Selector", key="back_to_materials_anode"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    st.markdown("### 🔋 Anode Materials Analysis")
    
    # Material selection
    # Check if material was passed from cell design workflow
    if 'selected_anode' in st.session_state:
        default_index = ['Graphite', 'Silicon', 'Tin'].index(st.session_state.selected_anode) if st.session_state.selected_anode in ['Graphite', 'Silicon', 'Tin'] else 0
    else:
        default_index = 0
    
    selected_anode = st.selectbox(
        "Select Anode Material:",
        options=['Graphite', 'Silicon', 'Tin', 'LTO', 'Graphite+SiO2'],
        index=default_index,
        key="anode_selector"
    )
    
    # Initialize session state for selected material
    coa_key = f"coa_data_{selected_anode}"
    if coa_key not in st.session_state:
        st.session_state[coa_key] = get_default_material_data(selected_anode)['coa_data']
    
    material_data = get_default_material_data(selected_anode)
    
    # Display material info
    st.markdown(f"**Selected Material:** {material_data['name']}")
    
    # CoA Data Editing Section
    st.markdown("#### CoA Data Editor")
    
    # Prepare data for the editable table
    coa_data = st.session_state[coa_key]
    editable_data = {
        'Category': [
            'Particle Size', 'Particle Size', 'Particle Size', 'Particle Size', 'Particle Size',
            'Surface & Density', 'Surface & Density', 'Surface & Density', 'Surface & Density',
            'Electrochemical', 'Electrochemical', 'Electrochemical', 'Electrochemical',
            'Chemical Composition', 'Chemical Composition', 'Chemical Composition', 'Chemical Composition'
        ],
        'Property': [
            'D-min (μm)', 'D10 (μm)', 'D50 (μm)', 'D90 (μm)', 'D-max (μm)',
            'BET Surface Area (m²/g)', 'Tap Density (g/cm³)', 'Bulk Density (g/cm³)', 'True Density (g/cm³)',
            'Specific Capacity (mAh/g)', 'Nominal Voltage (V)', 'Energy Density (Wh/kg)', 'Cycle Life (cycles)',
            'Moisture Content (%)', 'Total Impurities (ppm)', 'pH Value', 'Crystallinity (%)'
        ],
        'Value': [
            coa_data.get('D_min', 0.5), coa_data.get('D10', 2.1), coa_data.get('D50', 8.5),
            coa_data.get('D90', 18.2), coa_data.get('D_max', 45.0),
            coa_data.get('BET', 0.8), coa_data.get('tap_density', 2.4),
            coa_data.get('bulk_density', 1.8), coa_data.get('true_density', 2.2),
            coa_data.get('capacity', 372), coa_data.get('voltage', 0.1),
            coa_data.get('energy_density', 37), coa_data.get('cycle_life', 1000),
            coa_data.get('moisture', 0.02), coa_data.get('impurities', 50),
            coa_data.get('pH', 7.0), coa_data.get('crystallinity', 95.0)
        ]
    }
    
    edited_df = st.data_editor(
        pd.DataFrame(editable_data),
        column_config={
            "Category": st.column_config.TextColumn("Category", disabled=True),
            "Property": st.column_config.TextColumn("Property", disabled=True),
            "Value": st.column_config.NumberColumn("Value", step=0.01, format="%.3f")
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )
    
    # Extract values from edited table
    values = edited_df['Value'].tolist()
    d_min, d10, d50, d90, d_max = values[0:5]
    bet_surface, tap_density, bulk_density, true_density = values[5:9]
    capacity, voltage, energy_density, cycle_life = values[9:13]
    moisture, impurities, ph_value, crystallinity = values[13:17]
    
    # Update button
    if st.button("📊 Update CoA Data", key=f"update_coa_{selected_anode}", use_container_width=True):
        # Update session state with new values
        updated_coa_data = {
            'D_min': d_min, 'D10': d10, 'D50': d50, 'D90': d90, 'D_max': d_max,
            'BET': bet_surface, 'tap_density': tap_density, 'bulk_density': bulk_density, 'true_density': true_density,
            'capacity': capacity, 'voltage': voltage, 'energy_density': energy_density, 'cycle_life': cycle_life,
            'moisture': moisture, 'impurities': impurities, 'pH': ph_value, 'crystallinity': crystallinity
        }
        st.session_state[coa_key] = updated_coa_data
        st.success(f"✅ CoA data updated successfully for {selected_anode}")
        st.rerun()
    
    # PSD Plot Section
    st.markdown("#### Particle Size Distribution")
    
    # Create PSD plot
    try:
        from plotting import generate_psd_plot
        generate_psd_plot(st.session_state[coa_key], 'Both', selected_anode)
    except Exception as e:
        st.error(f"Error generating PSD plot: {str(e)}")
        st.info("Make sure scipy is installed: pip install scipy")
    
    # Performance plots
    st.markdown("#### Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # OCV plot
        soc = np.linspace(0, 100, 100)
        voltage = 0.1 + 0.3 * (soc/100) + 0.1 * np.sin(2 * np.pi * soc/50)
        
        fig = px.line(x=soc, y=voltage, title="OCV vs SOC")
        fig.update_layout(xaxis_title="State of Charge (%)", yaxis_title="Voltage (V)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cycle life plot
        cycles = np.linspace(0, 1000, 100)
        capacity_retention = 100 * np.exp(-cycles/2000)
        
        fig = px.line(x=cycles, y=capacity_retention, title="Cycle Life")
        fig.update_layout(xaxis_title="Cycle Number", yaxis_title="Capacity Retention (%)")
        st.plotly_chart(fig, use_container_width=True)


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
    from ai_assistant import render_chat_interface as ai_render_chat_interface
    ai_render_chat_interface()


def render_ocv_curves_page():
    """Render OCV curves analysis page"""
    st.markdown("### 🔋 OCV Curves Analysis")
    st.markdown("Realistic Open Circuit Voltage curves for battery materials")
    
    # Initialize OCV generator
    ocv_gen = OCVCurveGenerator()
    
    # Sidebar controls
    st.sidebar.header("Material Selection")
    
    # Get available materials from database
    available_materials = ocv_gen.get_available_materials()
    
    # Material selection
    material = st.sidebar.selectbox(
        "Select Material:",
        available_materials,
        format_func=lambda x: {
            "graphite": "Graphite (Anode)",
            "nmc811": "NMC811 (Cathode)",
            "lfp": "LFP (Cathode)",
            "nca": "NCA (Cathode)",
            "lto": "LTO (Anode)",
            "silicon": "Silicon (Anode)",
            "graphite_sio2": "Graphite+SiO2 (Anode)",
            "nmc532": "NMC532 (Cathode)",
            "lco": "LCO (Cathode)"
        }.get(x, x.title())
    )
    
    # Temperature control
    temperature = st.sidebar.slider(
        "Temperature (°C):",
        min_value=-20.0,
        max_value=60.0,
        value=25.0,
        step=1.0
    )
    
    # Display options
    st.sidebar.header("Display Options")
    show_plateaus = st.sidebar.checkbox("Show Plateaus", value=True)
    show_derivative = st.sidebar.checkbox("Show Derivative (dV/dQ)", value=False)
    
    # Material properties
    properties = ocv_gen.get_material_properties(material)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Material Properties")
        st.write(f"**Name**: {properties['name']}")
        st.write(f"**Type**: {properties['type'].title()}")
        st.write(f"**Voltage Range**: {properties['voltage_range'][0]:.2f} - {properties['voltage_range'][1]:.2f} V")
        st.write(f"**Capacity Range**: 0 - {properties['capacity_range'][1]} mAh/g")
        st.write(f"**Curve Type**: {properties['curve_type'].title()}")
    
    with col2:
        st.markdown("#### Key Features")
        if material == 'graphite':
            st.write("• **Staging Behavior**: Multiple voltage plateaus")
            st.write("• **Low Voltage**: 0.01 - 0.25 V vs Li/Li+")
            st.write("• **High Capacity**: Up to 372 mAh/g")
            st.write("• **Safety**: Low voltage reduces risk")
        else:
            st.write("• **High Voltage**: 3.0 - 4.3 V vs Li/Li+")
            st.write("• **Good Capacity**: 170 - 200 mAh/g")
            st.write("• **Stable**: Good cycle life")
            st.write("• **Energy Density**: High energy density")
    
    # Plot OCV curve
    st.markdown("#### OCV Curve")
    fig = ocv_gen.plot_ocv_curve(material, temperature, show_plateaus, show_derivative)
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparison plot
    if st.checkbox("Show Comparison with Other Materials"):
        st.markdown("#### Material Comparison")
        comparison_materials = st.multiselect(
            "Select materials to compare:",
            available_materials,
            default=[material, "nmc811"] if material != "nmc811" else [material, "graphite"]
        )
        
        if comparison_materials:
            comp_fig = ocv_gen.plot_comparison(comparison_materials, temperature)
            st.plotly_chart(comp_fig, use_container_width=True)
    
    # Technical details
    st.markdown("#### Technical Details")
    
    if material == 'graphite':
        st.markdown("""
        **Graphite OCV Characteristics:**
        - **Stage 1 (0-50 mAh/g)**: Dilute stage, ~0.05 V
        - **Stage 2 (50-150 mAh/g)**: Stage 2, ~0.08 V  
        - **Stage 3 (150-250 mAh/g)**: Stage 3, ~0.12 V
        - **Stage 4 (250-350 mAh/g)**: Stage 4, ~0.18 V
        - **High SOC (350-372 mAh/g)**: Rapid voltage increase
        
        The staging behavior is due to the intercalation of lithium ions into the graphite layers,
        creating ordered structures at different compositions.
        """)
    else:
        st.markdown(f"""
        **{properties['name']} OCV Characteristics:**
        - **Voltage Range**: {properties['voltage_range'][0]:.2f} - {properties['voltage_range'][1]:.2f} V
        - **Capacity**: Up to {properties['capacity_range'][1]} mAh/g
        - **Curve Shape**: {properties['curve_type'].title()} profile
        - **Applications**: High energy density batteries
        
        The OCV curve shows the relationship between state of charge and open circuit voltage,
        which is crucial for battery management systems.
        """)
    
    # Back button
    if st.button("← Back to Home", key="back_to_home_ocv"):
        st.session_state.current_page = 'home'
        st.rerun()


def render_anode_materials_page_new():
    """Render anode materials page with CoA and performance plots"""
    render_anode_page()


def render_cathode_materials_page_new():
    """Render cathode materials page with CoA and performance plots"""
    render_cathode_page()
