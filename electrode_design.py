"""
Electrode Design Functions for the Cell Development Platform
Handles electrode composition, material properties, and performance analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
from electrode_materials import ElectrodeMaterialManager


def render_cathode_electrode_design():
    """Render the cathode electrode design interface"""
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Cell Design", key="back_to_cell_design_cathode"):
            st.session_state.current_page = 'cell_design'
            st.rerun()
    
    with col2:
        if st.button("📋 Customize Material Properties", key="customize_cathode_material_detailed"):
            # Pass the selected material to the materials page
            if 'cell_design_workflow' in st.session_state:
                selected_material = st.session_state.cell_design_workflow.get('cathode_material', 'NMC811')
                st.session_state.selected_cathode = selected_material
            st.session_state.current_page = 'cathode_materials'
            st.rerun()
    
    with col3:
        if st.button("⏭️ Skip to Anode Design", key="skip_to_anode"):
            st.session_state.current_page = 'cell_design'
            if 'cell_design_workflow' in st.session_state:
                st.session_state.cell_design_workflow['current_step'] = 3
            st.rerun()
    
    st.markdown("### ⚡ Cathode Electrode Design")
    st.markdown("Design cathode electrode composition and analyze materials.")
    
    # Initialize electrode material manager
    if 'electrode_material_manager' not in st.session_state:
        st.session_state.electrode_material_manager = ElectrodeMaterialManager()
    
    material_manager = st.session_state.electrode_material_manager
    
    # Create two main columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Electrode Composition")
        
        # Active material selection with connection to cathode page
        cathode_materials = ["NMC811", "LCO", "NCA", "NMC622", "NMC532"]
        selected_cathode = st.selectbox("Active Material:", cathode_materials, key="cathode_active_material")
        
        if selected_cathode:
            st.session_state.selected_cathode = selected_cathode
            
            # Link to detailed cathode page
            if st.button(f"📋 View {selected_cathode} Details", key="view_cathode_details"):
                st.session_state.current_page = 'cathode_details'
                st.session_state.detailed_cathode = selected_cathode
                st.rerun()
        
        # Binder selection
        binder_options = material_manager.get_binder_options()
        selected_binder = st.selectbox("Binder:", binder_options, key="cathode_binder")
        
        # Conductive agent selection
        conductive_options = material_manager.get_conductive_agent_options()
        selected_conductive = st.selectbox("Conductive Agent:", conductive_options, key="cathode_conductive")
        
        # Foil material and thickness
        foil_options = material_manager.get_foil_material_options()
        selected_foil = st.selectbox("Foil Material:", foil_options, key="cathode_foil")
        
        if selected_foil:
            foil_props = material_manager.get_foil_material_properties(selected_foil)
            available_thicknesses = foil_props.get('available_thicknesses', [10, 15, 20, 25, 30])
            foil_thickness = st.selectbox("Foil Thickness (μm):", available_thicknesses, key="cathode_foil_thickness")
        else:
            foil_thickness = 20
        
        # Composition table
        st.markdown("#### Composition (wt%)")
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            active_wt = st.number_input("Active Material:", min_value=0.0, max_value=100.0, value=90.0, key="cathode_active_wt")
            binder_wt = st.number_input("Binder:", min_value=0.0, max_value=20.0, value=5.0, key="cathode_binder_wt")
        
        with comp_col2:
            conductive_wt = st.number_input("Conductive Agent:", min_value=0.0, max_value=20.0, value=5.0, key="cathode_conductive_wt")
            total_wt = active_wt + binder_wt + conductive_wt
            st.metric("Total", f"{total_wt:.1f}%")
        
        # Material properties display
        if selected_binder:
            st.markdown("#### Binder Properties")
            binder_props = material_manager.get_binder_properties(selected_binder)
            if binder_props:
                prop_df = pd.DataFrame([
                    {"Property": "Density", "Value": binder_props['properties']['density'], "Unit": "g/cm³"},
                    {"Property": "Molecular Weight", "Value": binder_props['properties']['molecular_weight'], "Unit": "g/mol"},
                    {"Property": "Tg", "Value": binder_props['properties']['glass_transition_temp'], "Unit": "°C"},
                    {"Property": "Tm", "Value": binder_props['properties']['melting_point'], "Unit": "°C"}
                ])
                st.dataframe(prop_df, hide_index=True, use_container_width=True)
        
        if selected_conductive:
            st.markdown("#### Conductive Agent Properties")
            conductive_props = material_manager.get_conductive_agent_properties(selected_conductive)
            if conductive_props:
                prop_df = pd.DataFrame([
                    {"Property": "Density", "Value": conductive_props['properties']['density'], "Unit": "g/cm³"},
                    {"Property": "Surface Area", "Value": conductive_props['properties']['specific_surface_area'], "Unit": "m²/g"},
                    {"Property": "Conductivity", "Value": conductive_props['properties']['electrical_conductivity'], "Unit": "S/cm"},
                    {"Property": "Particle Size", "Value": conductive_props['properties']['particle_size'], "Unit": "nm"}
                ])
                st.dataframe(prop_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("#### Calculated Properties")
        
        # Calculate electrode properties
        composition = {
            'active_material_wt': active_wt,
            'binder_wt': binder_wt,
            'conductive_wt': conductive_wt,
            'foil_thickness': foil_thickness,
            'active_material_density': 4.7,  # Default for NMC
            'binder_density': material_manager.get_binder_properties(selected_binder)['properties']['density'] if selected_binder else 1.78,
            'conductive_density': material_manager.get_conductive_agent_properties(selected_conductive)['properties']['density'] if selected_conductive else 2.1,
            'foil_density': material_manager.get_foil_material_properties(selected_foil)['properties']['density'] if selected_foil else 2.7
        }
        
        calculated_props = material_manager.calculate_electrode_properties(composition)
        
        if calculated_props:
            # Display calculated properties
            st.metric("Porosity", f"{calculated_props['porosity']:.1f}%")
            st.metric("Mass Loading", f"{calculated_props['mass_loading']:.1f} mg/cm²")
            st.metric("Calendared Thickness", f"{calculated_props['calendared_thickness']:.1f} μm")
            st.metric("Electrode Density", f"{calculated_props['electrode_density']:.2f} g/cm³")
            
            # Volume fractions
            st.markdown("#### Volume Fractions")
            vol_frac_df = pd.DataFrame([
                {"Component": "Active Material", "Volume %": f"{calculated_props['active_vol_frac']:.1f}%"},
                {"Component": "Binder", "Volume %": f"{calculated_props['binder_vol_frac']:.1f}%"},
                {"Component": "Conductive Agent", "Volume %": f"{calculated_props['conductive_vol_frac']:.1f}%"}
            ])
            st.dataframe(vol_frac_df, hide_index=True, use_container_width=True)
        
        # Customizable parameters
        st.markdown("#### Customizable Parameters")
        custom_porosity = st.slider("Target Porosity (%)", 20.0, 50.0, calculated_props.get('porosity', 40.0), key="cathode_porosity")
        target_mass_loading = st.slider("Target Mass Loading (mg/cm²)", 5.0, 30.0, calculated_props.get('mass_loading', 15.0), key="cathode_mass_loading")
        
        # Electrode thickness calculation
        if target_mass_loading and calculated_props.get('electrode_density'):
            calculated_thickness = (target_mass_loading / calculated_props['electrode_density']) * 10  # μm
            st.metric("Calculated Thickness", f"{calculated_thickness:.1f} μm")
    
    # Performance plots section
    st.markdown("---")
    st.markdown("#### Performance Analysis")
    
    # Create tabs for different performance views
    tab1, tab2, tab3 = st.tabs(["📊 Electrode Performance", "🔬 Material Properties", "📈 Export"])
    
    with tab1:
        # Electrode performance plots
        if st.button("Generate Performance Plots", key="gen_cathode_perf"):
            # Create performance plots based on composition
            create_electrode_performance_plots(selected_cathode, composition, calculated_props)
    
    with tab2:
        # Material properties analysis
        if selected_binder and 'functions' in material_manager.get_binder_properties(selected_binder):
            st.markdown("#### Binder Function Analysis")
            binder_data = material_manager.get_binder_properties(selected_binder)
            for func_name, func_data in binder_data['functions'].items():
                if st.button(f"Plot {func_name.replace('_', ' ').title()}", key=f"plot_binder_{func_name}"):
                    plot_material_function(func_name, func_data)
    
    with tab3:
        # Export functionality
        st.markdown("#### Export Electrode Design")
        if st.button("📥 Export Electrode Design", key="export_cathode_design"):
            export_data = {
                'active_material': selected_cathode,
                'binder': selected_binder,
                'conductive_agent': selected_conductive,
                'foil_material': selected_foil,
                'foil_thickness': foil_thickness,
                'composition': {
                    'active_material_wt': active_wt,
                    'binder_wt': binder_wt,
                    'conductive_wt': conductive_wt
                },
                'calculated_properties': calculated_props
            }
            
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="Download Electrode Design (JSON)",
                data=json_data,
                file_name=f"{selected_cathode}_electrode_design.json",
                mime="application/json"
            )


def render_anode_electrode_design():
    """Render the anode electrode design interface"""
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Cell Design", key="back_to_cell_design_anode"):
            st.session_state.current_page = 'cell_design'
            st.rerun()
    
    with col2:
        if st.button("📋 Customize Material Properties", key="customize_anode_material_detailed"):
            # Pass the selected material to the materials page
            if 'cell_design_workflow' in st.session_state:
                selected_material = st.session_state.cell_design_workflow.get('anode_material', 'Graphite')
                st.session_state.selected_anode = selected_material
            st.session_state.current_page = 'anode_materials'
            st.rerun()
    
    with col3:
        if st.button("⏭️ Skip to Electrolyte", key="skip_to_electrolyte"):
            st.session_state.current_page = 'cell_design'
            if 'cell_design_workflow' in st.session_state:
                st.session_state.cell_design_workflow['current_step'] = 4
            st.rerun()
    
    st.markdown("### 🔋 Anode Electrode Design")
    st.markdown("Design anode electrode composition and analyze materials.")
    
    # Initialize electrode material manager
    if 'electrode_material_manager' not in st.session_state:
        st.session_state.electrode_material_manager = ElectrodeMaterialManager()
    
    material_manager = st.session_state.electrode_material_manager
    
    # Create two main columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Electrode Composition")
        
        # Active material selection with connection to anode page
        anode_materials = ["Graphite", "Silicon", "Tin", "LTO", "Hard Carbon"]
        selected_anode = st.selectbox("Active Material:", anode_materials, key="anode_active_material")
        
        if selected_anode:
            st.session_state.selected_anode = selected_anode
            
            # Link to detailed anode page
            if st.button(f"📋 View {selected_anode} Details", key="view_anode_details"):
                st.session_state.current_page = 'anode_details'
                st.session_state.detailed_anode = selected_anode
                st.rerun()
        
        # Binder selection
        binder_options = material_manager.get_binder_options()
        selected_binder = st.selectbox("Binder:", binder_options, key="anode_binder")
        
        # Conductive agent selection
        conductive_options = material_manager.get_conductive_agent_options()
        selected_conductive = st.selectbox("Conductive Agent:", conductive_options, key="anode_conductive")
        
        # Foil material and thickness
        foil_options = material_manager.get_foil_material_options()
        selected_foil = st.selectbox("Foil Material:", foil_options, key="anode_foil")
        
        if selected_foil:
            foil_props = material_manager.get_foil_material_properties(selected_foil)
            available_thicknesses = foil_props.get('available_thicknesses', [6, 8, 10, 12, 15])
            foil_thickness = st.selectbox("Foil Thickness (μm):", available_thicknesses, key="anode_foil_thickness")
        else:
            foil_thickness = 10
        
        # Composition table
        st.markdown("#### Composition (wt%)")
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            active_wt = st.number_input("Active Material:", min_value=0.0, max_value=100.0, value=95.0, key="anode_active_wt")
            binder_wt = st.number_input("Binder:", min_value=0.0, max_value=20.0, value=3.0, key="anode_binder_wt")
        
        with comp_col2:
            conductive_wt = st.number_input("Conductive Agent:", min_value=0.0, max_value=20.0, value=2.0, key="anode_conductive_wt")
            total_wt = active_wt + binder_wt + conductive_wt
            st.metric("Total", f"{total_wt:.1f}%")
        
        # Material properties display
        if selected_binder:
            st.markdown("#### Binder Properties")
            binder_props = material_manager.get_binder_properties(selected_binder)
            if binder_props:
                prop_df = pd.DataFrame([
                    {"Property": "Density", "Value": binder_props['properties']['density'], "Unit": "g/cm³"},
                    {"Property": "Molecular Weight", "Value": binder_props['properties']['molecular_weight'], "Unit": "g/mol"},
                    {"Property": "Tg", "Value": binder_props['properties']['glass_transition_temp'], "Unit": "°C"},
                    {"Property": "Tm", "Value": binder_props['properties']['melting_point'], "Unit": "°C"}
                ])
                st.dataframe(prop_df, hide_index=True, use_container_width=True)
        
        if selected_conductive:
            st.markdown("#### Conductive Agent Properties")
            conductive_props = material_manager.get_conductive_agent_properties(selected_conductive)
            if conductive_props:
                prop_df = pd.DataFrame([
                    {"Property": "Density", "Value": conductive_props['properties']['density'], "Unit": "g/cm³"},
                    {"Property": "Surface Area", "Value": conductive_props['properties']['specific_surface_area'], "Unit": "m²/g"},
                    {"Property": "Conductivity", "Value": conductive_props['properties']['electrical_conductivity'], "Unit": "S/cm"},
                    {"Property": "Particle Size", "Value": conductive_props['properties']['particle_size'], "Unit": "nm"}
                ])
                st.dataframe(prop_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("#### Calculated Properties")
        
        # Calculate electrode properties
        composition = {
            'active_material_wt': active_wt,
            'binder_wt': binder_wt,
            'conductive_wt': conductive_wt,
            'foil_thickness': foil_thickness,
            'active_material_density': 2.2 if selected_anode == "Graphite" else 2.3,  # Default densities
            'binder_density': material_manager.get_binder_properties(selected_binder)['properties']['density'] if selected_binder else 1.78,
            'conductive_density': material_manager.get_conductive_agent_properties(selected_conductive)['properties']['density'] if selected_conductive else 2.1,
            'foil_density': material_manager.get_foil_material_properties(selected_foil)['properties']['density'] if selected_foil else 8.96
        }
        
        calculated_props = material_manager.calculate_electrode_properties(composition)
        
        if calculated_props:
            # Display calculated properties
            st.metric("Porosity", f"{calculated_props['porosity']:.1f}%")
            st.metric("Mass Loading", f"{calculated_props['mass_loading']:.1f} mg/cm²")
            st.metric("Calendared Thickness", f"{calculated_props['calendared_thickness']:.1f} μm")
            st.metric("Electrode Density", f"{calculated_props['electrode_density']:.2f} g/cm³")
            
            # Volume fractions
            st.markdown("#### Volume Fractions")
            vol_frac_df = pd.DataFrame([
                {"Component": "Active Material", "Volume %": f"{calculated_props['active_vol_frac']:.1f}%"},
                {"Component": "Binder", "Volume %": f"{calculated_props['binder_vol_frac']:.1f}%"},
                {"Component": "Conductive Agent", "Volume %": f"{calculated_props['conductive_vol_frac']:.1f}%"}
            ])
            st.dataframe(vol_frac_df, hide_index=True, use_container_width=True)
        
        # Customizable parameters
        st.markdown("#### Customizable Parameters")
        custom_porosity = st.slider("Target Porosity (%)", 20.0, 50.0, calculated_props.get('porosity', 40.0), key="anode_porosity")
        target_mass_loading = st.slider("Target Mass Loading (mg/cm²)", 5.0, 30.0, calculated_props.get('mass_loading', 15.0), key="anode_mass_loading")
        
        # Electrode thickness calculation
        if target_mass_loading and calculated_props.get('electrode_density'):
            calculated_thickness = (target_mass_loading / calculated_props['electrode_density']) * 10  # μm
            st.metric("Calculated Thickness", f"{calculated_thickness:.1f} μm")
    
    # Performance plots section
    st.markdown("---")
    st.markdown("#### Performance Analysis")
    
    # Create tabs for different performance views
    tab1, tab2, tab3 = st.tabs(["📊 Electrode Performance", "🔬 Material Properties", "📈 Export"])
    
    with tab1:
        # Electrode performance plots
        if st.button("Generate Performance Plots", key="gen_anode_perf"):
            # Create performance plots based on composition
            create_electrode_performance_plots(selected_anode, composition, calculated_props)
    
    with tab2:
        # Material properties analysis
        if selected_binder and 'functions' in material_manager.get_binder_properties(selected_binder):
            st.markdown("#### Binder Function Analysis")
            binder_data = material_manager.get_binder_properties(selected_binder)
            for func_name, func_data in binder_data['functions'].items():
                if st.button(f"Plot {func_name.replace('_', ' ').title()}", key=f"plot_anode_binder_{func_name}"):
                    plot_material_function(func_name, func_data)
    
    with tab3:
        # Export functionality
        st.markdown("#### Export Electrode Design")
        if st.button("📥 Export Electrode Design", key="export_anode_design"):
            export_data = {
                'active_material': selected_anode,
                'binder': selected_binder,
                'conductive_agent': selected_conductive,
                'foil_material': selected_foil,
                'foil_thickness': foil_thickness,
                'composition': {
                    'active_material_wt': active_wt,
                    'binder_wt': binder_wt,
                    'conductive_wt': conductive_wt
                },
                'calculated_properties': calculated_props
            }
            
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="Download Electrode Design (JSON)",
                data=json_data,
                file_name=f"{selected_anode}_electrode_design.json",
                mime="application/json"
            )


def create_electrode_performance_plots(material_name, composition, calculated_props):
    """Create performance plots for electrode design"""
    st.markdown("#### Electrode Performance Analysis")
    
    # Create subplots
    fig = go.Figure()
    
    # Simulate electrode performance data
    soc = np.linspace(0, 100, 100)
    
    if "cathode" in material_name.lower() or material_name in ["NMC811", "LCO", "NCA", "NMC622", "NMC532"]:
        # Cathode voltage profile
        voltage = 3.7 - 0.5 * (soc/100) + 0.2 * np.sin(2 * np.pi * soc/100)
        fig.add_trace(go.Scatter(x=soc, y=voltage, mode='lines', name='Voltage Profile', line=dict(color='blue')))
    else:
        # Anode voltage profile
        voltage = 0.1 + 0.3 * (soc/100) + 0.1 * np.sin(2 * np.pi * soc/50)
        fig.add_trace(go.Scatter(x=soc, y=voltage, mode='lines', name='Voltage Profile', line=dict(color='red')))
    
    fig.update_layout(
        title=f"{material_name} Electrode Performance",
        xaxis_title="State of Charge (%)",
        yaxis_title="Voltage (V)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Electrode properties summary
    if calculated_props:
        st.markdown("#### Electrode Properties Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Porosity", f"{calculated_props['porosity']:.1f}%")
        with col2:
            st.metric("Mass Loading", f"{calculated_props['mass_loading']:.1f} mg/cm²")
        with col3:
            st.metric("Thickness", f"{calculated_props['calendared_thickness']:.1f} μm")
        with col4:
            st.metric("Density", f"{calculated_props['electrode_density']:.2f} g/cm³")


def plot_material_function(func_name, func_data):
    """Plot material function"""
    import plotly.express as px
    
    if func_data['type'] == 'power_law':
        x_range = func_data['range']
        x = np.linspace(x_range[0], x_range[1], 100)
        params = func_data['parameters']
        y = params['K'] * (x ** params['n'])
    elif func_data['type'] == 'exponential_decay':
        x_range = func_data['range']
        x = np.linspace(x_range[0], x_range[1], 100)
        params = func_data['parameters']
        y = params['A'] * np.exp(-params['B'] * (x - params['C']))
    elif func_data['type'] == 'linear':
        x_range = func_data['range']
        x = np.linspace(x_range[0], x_range[1], 100)
        coeffs = func_data['coefficients']
        y = coeffs[0] + coeffs[1] * x
    else:
        x = np.linspace(0, 100, 100)
        y = np.zeros_like(x)
    
    fig = px.line(x=x, y=y, title=f"{func_name.replace('_', ' ').title()}")
    fig.update_layout(
        xaxis_title="Concentration (%)" if 'concentration' in func_name else "Temperature (°C)",
        yaxis_title=func_name.replace('_', ' ').title(),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
