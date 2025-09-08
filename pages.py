"""
Page rendering functions for the Cell Development Platform
"""
import streamlit as st
import pandas as pd
from material_data import get_default_material_data, get_default_anode_data
from utils import save_coa_to_json, create_excel_export
from plotting import generate_psd_plot, create_performance_plot, create_cycle_life_plots
from ai_assistant import EnhancedAIAssistant
from cell_design import CellDesignManager


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🔋 Cell Development Platform</h1>
        <p>Advanced battery material analysis and optimization tools</p>
    </div>
    """, unsafe_allow_html=True)


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
    """Render the cathode materials page with dropdown, table, and plots"""
    if st.button("← Back to Material Selector", key="back_to_materials"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    st.markdown("### Cathode Materials Analysis")
    
    # Material selection
    selected_cathode = st.selectbox(
        "Select Cathode Material:",
        options=['NMC811', 'LCO', 'NCA'],
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
        
        # Save to JSON file for plot functions
        json_filename = save_coa_to_json(updated_coa_data, selected_cathode)
        
        # Track action in AI context
        if 'ai_assistant' in st.session_state:
            st.session_state.ai_assistant.context_manager.add_recent_action(
                f"Updated CoA data for {selected_cathode}",
                {"material": selected_cathode, "filename": json_filename}
            )
        
        st.success(f"✅ CoA data updated successfully! Saved to {json_filename}")
        st.rerun()
    
    # PSD Plot Section
    st.markdown("#### Particle Size Distribution")
    psd_plot_type = st.selectbox(
        "Select PSD Plot Type:",
        options=['Normal Distribution', 'Cumulative Distribution', 'Both'],
        key=f"psd_plot_type_{selected_cathode}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate PSD plot
        try:
            generate_psd_plot(st.session_state[coa_key], psd_plot_type, selected_cathode)
        except Exception as e:
            st.error(f"Error generating PSD plot: {str(e)}")
            st.info("Make sure scipy is installed: pip install scipy")
    
    with col2:
        # Performance data plot selection
        plot_type = st.selectbox(
            "Select Performance Data:",
            options=['OCV', 'GITT', 'EIS'],
            key="performance_plot_type"
        )
        
        # Create performance plot
        fig = create_performance_plot(selected_cathode, plot_type, material_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Cycle life and coulombic efficiency plots
        col_cycle, col_eff = st.columns(2)
        
        with col_cycle:
            cycle_fig, eff_fig = create_cycle_life_plots(material_data)
            st.plotly_chart(cycle_fig, use_container_width=True)
        
        with col_eff:
            st.plotly_chart(eff_fig, use_container_width=True)
    
    # Export functionality
    st.markdown("#### Export Data")
    if st.button("📥 Export to Excel", key=f"export_{selected_cathode}"):
        try:
            excel_data = create_excel_export(material_data['name'], st.session_state[coa_key])
            st.download_button(
                label="Download Excel File",
                data=excel_data,
                file_name=f"{selected_cathode}_material_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error creating Excel export: {str(e)}")


def render_anode_materials_page():
    """Render the anode materials page with dropdown, table, and plots"""
    if st.button("← Back to Material Selector", key="back_to_materials_anode"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    st.markdown("### Anode Materials Analysis")
    
    # Material selection
    selected_anode = st.selectbox(
        "Select Anode Material:",
        options=['Graphite', 'Silicon', 'Tin'],
        key="anode_selector"
    )
    
    # Initialize session state for selected material
    coa_key = f"anode_coa_data_{selected_anode}"
    if coa_key not in st.session_state:
        st.session_state[coa_key] = get_default_anode_data(selected_anode)['coa_data']
    
    material_data = get_default_anode_data(selected_anode)
    
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
            coa_data.get('D_min', 5.0), coa_data.get('D10', 8.2), coa_data.get('D50', 15.5),
            coa_data.get('D90', 28.0), coa_data.get('D_max', 50.0),
            coa_data.get('BET', 2.5), coa_data.get('tap_density', 1.0),
            coa_data.get('bulk_density', 0.8), coa_data.get('true_density', 2.2),
            coa_data.get('capacity', 372), coa_data.get('voltage', 0.1),
            coa_data.get('energy_density', 37), coa_data.get('cycle_life', 2000),
            coa_data.get('moisture', 0.01), coa_data.get('impurities', 20),
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
    if st.button("📊 Update CoA Data", key=f"update_anode_coa_{selected_anode}", use_container_width=True):
        # Update session state with new values
        updated_coa_data = {
            'D_min': d_min, 'D10': d10, 'D50': d50, 'D90': d90, 'D_max': d_max,
            'BET': bet_surface, 'tap_density': tap_density, 'bulk_density': bulk_density, 'true_density': true_density,
            'capacity': capacity, 'voltage': voltage, 'energy_density': energy_density, 'cycle_life': cycle_life,
            'moisture': moisture, 'impurities': impurities, 'pH': ph_value, 'crystallinity': crystallinity
        }
        st.session_state[coa_key] = updated_coa_data
        
        # Save to JSON file for plot functions
        json_filename = save_coa_to_json(updated_coa_data, f"anode_{selected_anode}")
        
        # Track action in AI context
        if 'ai_assistant' in st.session_state:
            st.session_state.ai_assistant.context_manager.add_recent_action(
                f"Updated CoA data for anode {selected_anode}",
                {"material_type": "anode", "material": selected_anode, "filename": json_filename}
            )
        
        st.success(f"✅ CoA data updated successfully! Saved to {json_filename}")
        st.rerun()
    
    # PSD Plot Section
    st.markdown("#### Particle Size Distribution")
    psd_plot_type = st.selectbox(
        "Select PSD Plot Type:",
        options=['Normal Distribution', 'Cumulative Distribution', 'Both'],
        key=f"anode_psd_plot_type_{selected_anode}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate PSD plot
        try:
            generate_psd_plot(st.session_state[coa_key], psd_plot_type, f"anode_{selected_anode}")
        except Exception as e:
            st.error(f"Error generating PSD plot: {str(e)}")
            st.info("Make sure scipy is installed: pip install scipy")
    
    with col2:
        # Performance data plot selection
        plot_type = st.selectbox(
            "Select Performance Data:",
            options=['OCV', 'GITT', 'EIS'],
            key=f"anode_performance_plot_type_{selected_anode}"
        )
        
        # Create performance plot
        fig = create_performance_plot(f"anode_{selected_anode}", plot_type, material_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Export functionality
    st.markdown("#### Export Data")
    if st.button("📥 Export to Excel", key=f"export_anode_{selected_anode}"):
        try:
            excel_data = create_excel_export(material_data['name'], st.session_state[coa_key])
            st.download_button(
                label="Download Excel File",
                data=excel_data,
                file_name=f"anode_{selected_anode}_material_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error creating Excel export: {str(e)}")


def render_cell_design_page():
    """Render the cell design page with form factor selection and simulation"""
    if st.button("← Back to Home", key="back_to_home_cell_design"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("### 🔧 Cell Design")
    st.markdown("Design your battery cell by selecting form factor, electrodes, and components.")
    
    # Simple form factor selection first
    st.markdown("#### 🔋 Select Form Factor")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔋 Cylindrical", key="cylindrical_btn", use_container_width=True):
            st.session_state.selected_form_factor = "cylindrical"
            st.rerun()
    
    with col2:
        if st.button("📱 Pouch", key="pouch_btn", use_container_width=True):
            st.session_state.selected_form_factor = "pouch"
            st.rerun()
    
    with col3:
        if st.button("📦 Prismatic", key="prismatic_btn", use_container_width=True):
            st.session_state.selected_form_factor = "prismatic"
            st.rerun()
    
    # Show selected form factor
    if 'selected_form_factor' in st.session_state and st.session_state.selected_form_factor:
        st.success(f"Selected: {st.session_state.selected_form_factor.title()}")
        
        # Show dimensions based on form factor
        if st.session_state.selected_form_factor == "cylindrical":
            st.markdown("#### Cylindrical Cell Dimensions")
            diameter = st.slider("Diameter (mm)", 10.0, 50.0, 18.0, key="cyl_diameter")
            height = st.slider("Height (mm)", 30.0, 150.0, 65.0, key="cyl_height")
            volume = 3.14159 * (diameter/2)**2 * height / 1000
            st.metric("Volume", f"{volume:.2f} cm³")
            
        elif st.session_state.selected_form_factor == "pouch":
            st.markdown("#### Pouch Cell Dimensions")
            height = st.slider("Height (mm)", 50.0, 200.0, 100.0, key="pouch_height")
            width = st.slider("Width (mm)", 30.0, 150.0, 60.0, key="pouch_width")
            length = st.slider("Length (mm)", 2.0, 50.0, 5.0, key="pouch_length")
            volume = height * width * length / 1000
            st.metric("Volume", f"{volume:.2f} cm³")
            
        elif st.session_state.selected_form_factor == "prismatic":
            st.markdown("#### Prismatic Cell Dimensions")
            height = st.slider("Height (mm)", 50.0, 200.0, 100.0, key="prism_height")
            width = st.slider("Width (mm)", 30.0, 150.0, 60.0, key="prism_width")
            length = st.slider("Length (mm)", 2.0, 50.0, 20.0, key="prism_length")
            volume = height * width * length / 1000
            st.metric("Volume", f"{volume:.2f} cm³")
    
    # Electrode selection
    st.markdown("#### ⚡ Select Electrodes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cathode = st.selectbox("Cathode Material:", ["NMC811", "LCO", "NCA"], key="cathode_select")
        st.write(f"Selected cathode: {cathode}")
    
    with col2:
        anode = st.selectbox("Anode Material:", ["Graphite", "Silicon", "Tin"], key="anode_select")
        st.write(f"Selected anode: {anode}")
    
    # Electrolyte and separator
    st.markdown("#### 💧 Select Electrolyte & Separator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        electrolyte = st.selectbox("Electrolyte:", ["LiPF6 in EC:DMC", "LiPF6 in EC:EMC", "LiTFSI in EC:DMC"], key="electrolyte_select")
        st.write(f"Selected electrolyte: {electrolyte}")
    
    with col2:
        separator = st.selectbox("Separator:", ["PE", "PP", "PE/PP Trilayer"], key="separator_select")
        st.write(f"Selected separator: {separator}")
    
    # Simulation
    st.markdown("#### 🔬 Simulation")
    
    if st.button("🚀 Run Simulation", key="run_sim", use_container_width=True):
        if 'selected_form_factor' in st.session_state and st.session_state.selected_form_factor:
            st.success("✅ Simulation completed!")
            st.write("**Results:**")
            st.write("- Estimated Capacity: 2.5 Ah")
            st.write("- Energy Density: 9.25 Wh")
            st.write("- Cycle Life: 1000+ cycles")
            
            # Simple performance plot
            import plotly.express as px
            import numpy as np
            
            soc = np.linspace(0, 100, 100)
            voltage = 3.7 - 0.5 * (soc/100) + 0.2 * np.sin(2 * np.pi * soc/100)
            
            fig = px.line(x=soc, y=voltage, title="Voltage vs State of Charge")
            fig.update_layout(xaxis_title="State of Charge (%)", yaxis_title="Voltage (V)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select a form factor first!")


def render_chat_interface():
    """Render the enhanced chat interface with context awareness"""
    st.markdown("### 🤖 AI Assistant")
    
    # Initialize AI assistant
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = EnhancedAIAssistant()
    
    ai_assistant = st.session_state.ai_assistant
    
    # Show current context
    with st.expander("📍 Current Context", expanded=False):
        current_page = st.session_state.get('current_page', 'home')
        selected_materials = {}
        
        # Get selected materials from session state
        for key in st.session_state.keys():
            if key.startswith('coa_data_') or key.startswith('anode_coa_data_'):
                material_name = key.replace('coa_data_', '').replace('anode_coa_data_', '')
                if 'anode_coa_data_' in key:
                    selected_materials['anode'] = material_name
                else:
                    selected_materials['cathode'] = material_name
        
        st.write(f"**Current Page:** {current_page}")
        if selected_materials:
            st.write(f"**Selected Materials:** {selected_materials}")
        else:
            st.write("**Selected Materials:** None")
        
        # Show recent actions
        recent_actions = ai_assistant.get_recent_actions()
        if recent_actions:
            st.write("**Recent Actions:**")
            for action in recent_actions[:3]:
                st.write(f"• {action['action']}")
    
    # Show contextual suggestions
    suggestions = ai_assistant.get_contextual_suggestions(current_page)
    if suggestions:
        st.markdown("💡 **Suggestions:**")
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
    
    # Chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about battery materials..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response with context awareness
        current_page = st.session_state.get('current_page', 'home')
        selected_materials = {}
        
        # Get selected materials from session state
        for key in st.session_state.keys():
            if key.startswith('coa_data_') or key.startswith('anode_coa_data_'):
                material_name = key.replace('coa_data_', '').replace('anode_coa_data_', '')
                if 'anode_coa_data_' in key:
                    selected_materials['anode'] = material_name
                else:
                    selected_materials['cathode'] = material_name
        
        # Generate response using enhanced AI assistant
        response = ai_assistant.generate_response(prompt, current_page, selected_materials)
        
        # Check if response contains navigation commands
        if any(word in response.lower() for word in ["i'll take you", "navigate", "go to"]):
            # Extract navigation intent and execute
            if "home" in response.lower():
                st.session_state.current_page = 'home'
                st.rerun()
            elif "material selector" in response.lower():
                st.session_state.current_page = 'material_selector'
                st.rerun()
            elif "cathode" in response.lower():
                st.session_state.current_page = 'cathode_materials'
                st.rerun()
            elif "anode" in response.lower():
                st.session_state.current_page = 'anode_materials'
                st.rerun()
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)


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
    
    elif "anode" in prompt_lower:
        st.session_state.current_page = 'anode_materials'
        st.rerun()
        return "Opening Anode Materials page..."
    
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
