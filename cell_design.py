"""
Cell Design Module for the Cell Development Platform
Handles comprehensive cell design workflow with breadcrumb navigation
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Optional


class CellDesignManager:
    """Manages comprehensive cell design workflow with breadcrumb navigation"""
    
    def __init__(self):
        # Initialize workflow steps
        self.workflow_steps = [
            "form_factor",
            "casing_material", 
            "cathode_electrode_design",
            "anode_electrode_design",
            "electrolyte_separator",
            "safety_features",
            "simulation"
        ]
        
        # Form factor definitions with 2D schematics
        self.form_factors = {
            "cylindrical": {
                "name": "Cylindrical",
                "description": "High energy density, good thermal management",
                "dimensions": {"diameter": 18.0, "height": 65.0},
                "schematic": "cylindrical_2d",
                "volume": 0.0
            },
            "pouch": {
                "name": "Pouch",
                "description": "Flexible shape, lightweight",
                "dimensions": {"height": 100.0, "width": 60.0, "length": 5.0},
                "schematic": "pouch_2d",
                "volume": 0.0
            },
            "prismatic": {
                "name": "Prismatic",
                "description": "Good space utilization, thermal management",
                "dimensions": {"height": 100.0, "width": 60.0, "length": 20.0},
                "schematic": "prismatic_2d",
                "volume": 0.0
            }
        }
        
        # Initialize material library path
        self.material_lib_path = "material_lib"
        self._ensure_material_lib_exists()
        
        # Load casing materials
        self.casing_materials = self._load_casing_materials()
        
        # Initialize workflow state
        if 'cell_design_workflow' not in st.session_state:
            st.session_state.cell_design_workflow = {
                'current_step': 0,
                'form_factor': None,
                'casing_material': None,
                'cathode_material': None,
                'anode_material': None,
                'electrolyte': None,
                'separator': None,
                'safety_features': {},
                'simulation_results': {}
            }
    
    def _ensure_material_lib_exists(self):
        """Ensure material library directory exists"""
        if not os.path.exists(self.material_lib_path):
            os.makedirs(self.material_lib_path)
            self._create_default_casing_materials()
    
    def _create_default_casing_materials(self):
        """Create default casing material library"""
        default_materials = {
            "Aluminum_3003": {
                "name": "Aluminum 3003",
                "type": "metal",
                "properties": {
                    "density": 2.73,  # g/cm³
                    "thermal_conductivity": 193,  # W/m·K
                    "electrical_conductivity": 3.5e7,  # S/m
                    "yield_strength": 145,  # MPa
                    "tensile_strength": 186,  # MPa
                    "melting_point": 655,  # °C
                    "thermal_expansion": 23.2e-6,  # 1/K
                    "corrosion_resistance": "excellent"
                },
                "functions": {
                    "thermal_conductivity_vs_temp": {
                        "type": "polynomial",
                        "coefficients": [193, -0.05, 0.0001],
                        "range": [20, 200]
                    },
                    "yield_strength_vs_temp": {
                        "type": "exponential_decay",
                        "parameters": {"A": 145, "B": 0.01, "C": 100},
                        "range": [20, 300]
                    }
                }
            },
            "Steel_316L": {
                "name": "Stainless Steel 316L",
                "type": "metal",
                "properties": {
                    "density": 8.0,
                    "thermal_conductivity": 16,
                    "electrical_conductivity": 1.4e6,
                    "yield_strength": 290,
                    "tensile_strength": 580,
                    "melting_point": 1400,
                    "thermal_expansion": 16.0e-6,
                    "corrosion_resistance": "excellent"
                },
                "functions": {
                    "thermal_conductivity_vs_temp": {
                        "type": "linear",
                        "coefficients": [16, 0.02],
                        "range": [20, 500]
                    }
                }
            },
            "Carbon_Fiber_Composite": {
                "name": "Carbon Fiber Composite",
                "type": "composite",
                "properties": {
                    "density": 1.6,
                    "thermal_conductivity": 150,
                    "electrical_conductivity": 1e4,
                    "yield_strength": 800,
                    "tensile_strength": 1200,
                    "melting_point": 3500,
                    "thermal_expansion": 0.5e-6,
                    "corrosion_resistance": "excellent"
                },
                "functions": {
                    "thermal_conductivity_vs_temp": {
                        "type": "constant",
                        "value": 150,
                        "range": [20, 200]
                    }
                }
            }
        }
        
        for material_name, material_data in default_materials.items():
            file_path = os.path.join(self.material_lib_path, f"{material_name}.json")
            with open(file_path, 'w') as f:
                json.dump(material_data, f, indent=2)
    
    def _load_casing_materials(self):
        """Load casing materials from material library"""
        materials = {}
        if os.path.exists(self.material_lib_path):
            for filename in os.listdir(self.material_lib_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.material_lib_path, filename)
                    with open(file_path, 'r') as f:
                        material_data = json.load(f)
                        materials[filename[:-5]] = material_data
        return materials
    
    def render_breadcrumb_navigation(self):
        """Render breadcrumb navigation for workflow steps"""
        workflow = st.session_state.cell_design_workflow
        current_step = workflow['current_step']
        
        # Create breadcrumb
        breadcrumb_html = '<div style="background: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">'
        breadcrumb_html += '<div style="display: flex; align-items: center; gap: 10px;">'
        
        step_names = {
            0: "Form Factor",
            1: "Casing Material", 
            2: "Cathode Electrode",
            3: "Anode Electrode",
            4: "Electrolyte & Separator",
            5: "Safety Features",
            6: "Simulation"
        }
        
        for i, step in enumerate(self.workflow_steps):
            if i <= current_step:
                # Completed or current step
                color = "#1f77b4" if i == current_step else "#2ca02c"
                weight = "bold" if i == current_step else "normal"
                breadcrumb_html += f'<span style="color: {color}; font-weight: {weight};">{step_names[i]}</span>'
            else:
                # Future step
                breadcrumb_html += f'<span style="color: #ccc;">{step_names[i]}</span>'
            
            if i < len(self.workflow_steps) - 1:
                breadcrumb_html += '<span style="color: #ccc;"> → </span>'
        
        breadcrumb_html += '</div></div>'
        st.markdown(breadcrumb_html, unsafe_allow_html=True)
    
    def render_form_factor_selection(self):
        """Render form factor selection with 2D schematics"""
        st.markdown("### 🔋 Select Form Factor")
        st.markdown("Choose the cell form factor and adjust dimensions:")
        
        workflow = st.session_state.cell_design_workflow
        
        # Create three columns for form factors
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self._render_form_factor_card("cylindrical", col1)
        
        with col2:
            self._render_form_factor_card("pouch", col2)
        
        with col3:
            self._render_form_factor_card("prismatic", col3)
        
        # Show selected form factor details
        if workflow['form_factor']:
            self._render_form_factor_details()
    
    def _render_form_factor_card(self, form_factor_key: str, column):
        """Render individual form factor card with 2D schematic"""
        form_factor = self.form_factors[form_factor_key]
        workflow = st.session_state.cell_design_workflow
        is_selected = workflow['form_factor'] == form_factor_key
        
        # Card styling
        border_color = "#1f77b4" if is_selected else "#e0e0e0"
        background_color = "#f0f8ff" if is_selected else "#ffffff"
        
        with column:
            st.markdown(f"""
            <div style="
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 20px;
                background-color: {background_color};
                text-align: center;
                cursor: pointer;
                margin-bottom: 10px;
            ">
                <h3>{form_factor['name']}</h3>
                <p>{form_factor['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 2D Schematic
            self._render_2d_schematic(form_factor_key)
            
            # Selection button
            if st.button(f"Select {form_factor['name']}", key=f"select_{form_factor_key}", use_container_width=True):
                workflow['form_factor'] = form_factor_key
                st.rerun()
    
    def _render_2d_schematic(self, form_factor_key: str):
        """Render 2D schematic for form factor"""
        if form_factor_key == "cylindrical":
            self._render_cylindrical_schematic()
        elif form_factor_key == "pouch":
            self._render_pouch_schematic()
        elif form_factor_key == "prismatic":
            self._render_prismatic_schematic()
    
    def _render_cylindrical_schematic(self):
        """Render 2D cylindrical cell schematic"""
        fig = go.Figure()
        
        # Outer cylinder
        theta = np.linspace(0, 2*np.pi, 100)
        x_outer = 0.5 * np.cos(theta)
        y_outer = 0.5 * np.sin(theta)
        
        # Inner cylinder (empty space)
        x_inner = 0.3 * np.cos(theta)
        y_inner = 0.3 * np.sin(theta)
        
        # Add traces
        fig.add_trace(go.Scatter(x=x_outer, y=y_outer, fill='toself', 
                                fillcolor='lightblue', line=dict(color='blue', width=2),
                                name='Casing'))
        fig.add_trace(go.Scatter(x=x_inner, y=y_inner, fill='toself',
                                fillcolor='white', line=dict(color='gray', width=1),
                                name='Interior'))
        
        # Add dimensions
        fig.add_annotation(x=0, y=0.6, text="D", showarrow=True, arrowhead=2, 
                          arrowcolor="red", ax=0, ay=-20)
        fig.add_annotation(x=0.6, y=0, text="H", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=20, ay=0)
        
        fig.update_layout(
            title="Cylindrical Cell",
            xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            showlegend=False,
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_pouch_schematic(self):
        """Render 2D pouch cell schematic"""
        fig = go.Figure()
        
        # Pouch outline
        x_pouch = [-0.4, 0.4, 0.4, -0.4, -0.4]
        y_pouch = [-0.2, -0.2, 0.2, 0.2, -0.2]
        
        # Tabs
        x_tab1 = [-0.1, 0.1, 0.1, -0.1, -0.1]
        y_tab1 = [0.2, 0.2, 0.3, 0.3, 0.2]
        
        x_tab2 = [-0.1, 0.1, 0.1, -0.1, -0.1]
        y_tab2 = [-0.2, -0.2, -0.3, -0.3, -0.2]
        
        fig.add_trace(go.Scatter(x=x_pouch, y=y_pouch, fill='toself',
                                fillcolor='lightgreen', line=dict(color='green', width=2),
                                name='Pouch'))
        fig.add_trace(go.Scatter(x=x_tab1, y=y_tab1, fill='toself',
                                fillcolor='darkgreen', line=dict(color='green', width=1),
                                name='Tab+'))
        fig.add_trace(go.Scatter(x=x_tab2, y=y_tab2, fill='toself',
                                fillcolor='darkgreen', line=dict(color='green', width=1),
                                name='Tab-'))
        
        # Add dimensions
        fig.add_annotation(x=0, y=0.35, text="H", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=0, ay=-10)
        fig.add_annotation(x=0.45, y=0, text="W", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=-10, ay=0)
        fig.add_annotation(x=0, y=0, text="L", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=0, ay=0, arrowside="end")
        
        fig.update_layout(
            title="Pouch Cell",
            xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            showlegend=False,
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_prismatic_schematic(self):
        """Render 2D prismatic cell schematic"""
        fig = go.Figure()
        
        # Prismatic outline
        x_prism = [-0.4, 0.4, 0.4, -0.4, -0.4]
        y_prism = [-0.2, -0.2, 0.2, 0.2, -0.2]
        
        # Terminals
        x_term1 = [-0.05, 0.05, 0.05, -0.05, -0.05]
        y_term1 = [0.2, 0.2, 0.25, 0.25, 0.2]
        
        x_term2 = [-0.05, 0.05, 0.05, -0.05, -0.05]
        y_term2 = [-0.2, -0.2, -0.25, -0.25, -0.2]
        
        fig.add_trace(go.Scatter(x=x_prism, y=y_prism, fill='toself',
                                fillcolor='lightcoral', line=dict(color='red', width=2),
                                name='Prismatic'))
        fig.add_trace(go.Scatter(x=x_term1, y=y_term1, fill='toself',
                                fillcolor='darkred', line=dict(color='red', width=1),
                                name='Terminal+'))
        fig.add_trace(go.Scatter(x=x_term2, y=y_term2, fill='toself',
                                fillcolor='darkred', line=dict(color='red', width=1),
                                name='Terminal-'))
        
        # Add dimensions
        fig.add_annotation(x=0, y=0.3, text="H", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=0, ay=-10)
        fig.add_annotation(x=0.45, y=0, text="W", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=-10, ay=0)
        fig.add_annotation(x=0, y=0, text="L", showarrow=True, arrowhead=2,
                          arrowcolor="red", ax=0, ay=0, arrowside="end")
        
        fig.update_layout(
            title="Prismatic Cell",
            xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            showlegend=False,
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_form_factor_details(self):
        """Render form factor dimension inputs and details"""
        workflow = st.session_state.cell_design_workflow
        form_factor_key = workflow['form_factor']
        form_factor = self.form_factors[form_factor_key]
        
        st.success(f"Selected: {form_factor['name']}")
        
        # Dimension inputs
        if form_factor_key == "cylindrical":
            st.markdown("#### Cylindrical Cell Dimensions")
            col1, col2 = st.columns(2)
            
            with col1:
                diameter = st.slider("Diameter (mm)", 10.0, 50.0, form_factor['dimensions']['diameter'], key="cyl_diameter")
                form_factor['dimensions']['diameter'] = diameter
            
            with col2:
                height = st.slider("Height (mm)", 30.0, 150.0, form_factor['dimensions']['height'], key="cyl_height")
                form_factor['dimensions']['height'] = height
            
            # Calculate volume
            volume = 3.14159 * (diameter/2)**2 * height / 1000
            form_factor['volume'] = volume
            st.metric("Volume", f"{volume:.2f} cm³")
            
        elif form_factor_key == "pouch":
            st.markdown("#### Pouch Cell Dimensions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                height = st.slider("Height (mm)", 50.0, 200.0, form_factor['dimensions']['height'], key="pouch_height")
                form_factor['dimensions']['height'] = height
            
            with col2:
                width = st.slider("Width (mm)", 30.0, 150.0, form_factor['dimensions']['width'], key="pouch_width")
                form_factor['dimensions']['width'] = width
            
            with col3:
                length = st.slider("Length (mm)", 2.0, 50.0, form_factor['dimensions']['length'], key="pouch_length")
                form_factor['dimensions']['length'] = length
            
            # Calculate volume
            volume = height * width * length / 1000
            form_factor['volume'] = volume
            st.metric("Volume", f"{volume:.2f} cm³")
            
        elif form_factor_key == "prismatic":
            st.markdown("#### Prismatic Cell Dimensions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                height = st.slider("Height (mm)", 50.0, 200.0, form_factor['dimensions']['height'], key="prism_height")
                form_factor['dimensions']['height'] = height
            
            with col2:
                width = st.slider("Width (mm)", 30.0, 150.0, form_factor['dimensions']['width'], key="prism_width")
                form_factor['dimensions']['width'] = width
            
            with col3:
                length = st.slider("Length (mm)", 2.0, 50.0, form_factor['dimensions']['length'], key="prism_length")
                form_factor['dimensions']['length'] = length
            
            # Calculate volume
            volume = height * width * length / 1000
            form_factor['volume'] = volume
            st.metric("Volume", f"{volume:.2f} cm³")
        
        # Next button
        if st.button("Next: Select Casing Material", key="next_casing", use_container_width=True):
            workflow['current_step'] = 1
            st.rerun()
    
    def render_workflow_step(self):
        """Render current workflow step"""
        workflow = st.session_state.cell_design_workflow
        current_step = workflow['current_step']
        
        # Render breadcrumb navigation
        self.render_breadcrumb_navigation()
        
        # Render appropriate step
        if current_step == 0:
            self.render_form_factor_selection()
        elif current_step == 1:
            self.render_casing_material_selection()
        elif current_step == 2:
            self.render_cathode_electrode_design()
        elif current_step == 3:
            self.render_anode_electrode_design()
        elif current_step == 4:
            self.render_electrolyte_separator_selection()
        elif current_step == 5:
            self.render_safety_features_selection()
        elif current_step == 6:
            self.render_simulation()
    
    def render_casing_material_selection(self):
        """Render casing material selection with material library"""
        st.markdown("### 🏗️ Select Casing Material")
        st.markdown("Choose casing material and review electro-thermo-mechanical properties:")
        
        workflow = st.session_state.cell_design_workflow
        
        # Material selection dropdown
        material_options = list(self.casing_materials.keys())
        selected_material = st.selectbox(
            "Select Casing Material:",
            material_options,
            key="casing_material_select"
        )
        
        if selected_material:
            workflow['casing_material'] = selected_material
            material_data = self.casing_materials[selected_material]
            
            # Display material properties
            st.markdown(f"#### {material_data['name']} Properties")
            
            # Create editable properties table
            properties_data = []
            for prop, value in material_data['properties'].items():
                properties_data.append({
                    "Property": prop.replace('_', ' ').title(),
                    "Value": value,
                    "Unit": self._get_property_unit(prop)
                })
            
            df = pd.DataFrame(properties_data)
            edited_df = st.data_editor(
                df,
                column_config={
                    "Property": st.column_config.TextColumn("Property", disabled=True),
                    "Value": st.column_config.NumberColumn("Value", step=0.01, format="%.3f"),
                    "Unit": st.column_config.TextColumn("Unit", disabled=True)
                },
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )
            
            # Functions section
            if 'functions' in material_data and material_data['functions']:
                st.markdown("#### Material Functions")
                for func_name, func_data in material_data['functions'].items():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**{func_name.replace('_', ' ').title()}**")
                        st.write(f"Type: {func_data['type']}")
                        st.write(f"Range: {func_data['range'][0]}°C to {func_data['range'][1]}°C")
                    
                    with col2:
                        if st.button(f"Plot {func_name}", key=f"plot_{func_name}"):
                            self._plot_material_function(func_name, func_data)
            
            # Next button
            if st.button("Next: Select Cathode Material", key="next_cathode", use_container_width=True):
                workflow['current_step'] = 2
                st.rerun()
    
    def _get_property_unit(self, property_name: str) -> str:
        """Get unit for material property"""
        units = {
            'density': 'g/cm³',
            'thermal_conductivity': 'W/m·K',
            'electrical_conductivity': 'S/m',
            'yield_strength': 'MPa',
            'tensile_strength': 'MPa',
            'melting_point': '°C',
            'thermal_expansion': '1/K',
            'corrosion_resistance': 'rating'
        }
        return units.get(property_name, '')
    
    def _plot_material_function(self, func_name: str, func_data: dict):
        """Plot material function"""
        temp_range = func_data['range']
        temps = np.linspace(temp_range[0], temp_range[1], 100)
        
        if func_data['type'] == 'polynomial':
            coeffs = func_data['coefficients']
            values = np.polyval(coeffs, temps)
        elif func_data['type'] == 'linear':
            coeffs = func_data['coefficients']
            values = coeffs[0] + coeffs[1] * temps
        elif func_data['type'] == 'exponential_decay':
            params = func_data['parameters']
            values = params['A'] * np.exp(-params['B'] * (temps - params['C']))
        elif func_data['type'] == 'constant':
            values = np.full_like(temps, func_data['value'])
        else:
            values = np.zeros_like(temps)
        
        fig = px.line(x=temps, y=values, title=f"{func_name.replace('_', ' ').title()}")
        fig.update_layout(
            xaxis_title="Temperature (°C)",
            yaxis_title=func_name.replace('_', ' ').title(),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_cathode_material_selection(self):
        """Render cathode material selection with electrode design option"""
        st.markdown("### ⚡ Select Cathode Material")
        
        workflow = st.session_state.cell_design_workflow
        
        # Quick selection for workflow
        cathode_options = ["NMC811", "LCO", "NCA", "NMC622", "NMC532"]
        selected_cathode = st.selectbox("Select Cathode Material:", cathode_options, key="workflow_cathode")
        
        if selected_cathode:
            workflow['cathode_material'] = selected_cathode
            st.success(f"Selected: {selected_cathode}")
        
        # Electrode design option
        st.markdown("#### Electrode Design")
        st.info("Design the cathode electrode composition, porosity, mass loading, and density")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔧 Design Cathode Electrode", key="design_cathode_electrode", use_container_width=True):
                workflow['current_step'] = 3
                st.rerun()
        
        with col2:
            if st.button("📋 View Material Details", key="view_cathode_details", use_container_width=True):
                st.session_state.current_page = 'cathode_materials'
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip Electrode Design", key="skip_cathode_electrode", use_container_width=True):
                workflow['current_step'] = 4
                st.rerun()
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Casing Material", key="prev_casing"):
                workflow['current_step'] = 1
                st.rerun()
        
        with col2:
            if st.button("Next: Select Anode Material →", key="next_anode", use_container_width=True):
                workflow['current_step'] = 4
                st.rerun()
    
    def render_cathode_electrode_design(self):
        """Render cathode electrode design with material selection"""
        st.markdown("### ⚡ Cathode Electrode Design")
        st.markdown("Select cathode material and design electrode composition, porosity, mass loading, and density")
        
        workflow = st.session_state.cell_design_workflow
        
        # Material selection
        cathode_options = ["NMC811", "LCO", "NCA", "NMC622", "NMC532"]
        selected_cathode = st.selectbox("Select Cathode Material:", cathode_options, key="workflow_cathode")
        
        if selected_cathode:
            workflow['cathode_material'] = selected_cathode
            st.success(f"Selected: {selected_cathode}")
        
        # Electrode design options
        st.markdown("#### Electrode Design Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔧 Design Electrode Composition", key="design_cathode_electrode", use_container_width=True):
                st.session_state.current_page = 'cathode_electrode_design'
                st.rerun()
        
        with col2:
            if st.button("📋 Customize Material Properties", key="customize_cathode_material", use_container_width=True):
                # Pass the selected material to the materials page
                st.session_state.selected_cathode = selected_cathode
                st.session_state.current_page = 'cathode_materials'
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip Electrode Design", key="skip_cathode_electrode", use_container_width=True):
                workflow['current_step'] = 3
                st.rerun()
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Casing Material", key="prev_casing"):
                workflow['current_step'] = 1
                st.rerun()
        
        with col2:
            if st.button("Next: Anode Electrode Design →", key="next_anode", use_container_width=True):
                workflow['current_step'] = 3
                st.rerun()
    
    def render_anode_electrode_design(self):
        """Render anode electrode design with material selection"""
        st.markdown("### 🔋 Anode Electrode Design")
        st.markdown("Select anode material and design electrode composition, porosity, mass loading, and density")
        
        workflow = st.session_state.cell_design_workflow
        
        # Material selection
        anode_options = ["Graphite", "Silicon", "Tin", "LTO", "Hard Carbon"]
        selected_anode = st.selectbox("Select Anode Material:", anode_options, key="workflow_anode")
        
        if selected_anode:
            workflow['anode_material'] = selected_anode
            st.success(f"Selected: {selected_anode}")
        
        # Electrode design options
        st.markdown("#### Electrode Design Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔧 Design Electrode Composition", key="design_anode_electrode", use_container_width=True):
                st.session_state.current_page = 'anode_electrode_design'
                st.rerun()
        
        with col2:
            if st.button("📋 Customize Material Properties", key="customize_anode_material", use_container_width=True):
                # Pass the selected material to the materials page
                st.session_state.selected_anode = selected_anode
                st.session_state.current_page = 'anode_materials'
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip Electrode Design", key="skip_anode_electrode", use_container_width=True):
                workflow['current_step'] = 4
                st.rerun()
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Cathode Electrode", key="prev_cathode"):
                workflow['current_step'] = 2
                st.rerun()
        
        with col2:
            if st.button("Next: Electrolyte & Separator →", key="next_electrolyte", use_container_width=True):
                workflow['current_step'] = 4
                st.rerun()
    
    def render_anode_material_selection(self):
        """Render anode material selection with electrode design option"""
        st.markdown("### 🔋 Select Anode Material")
        
        workflow = st.session_state.cell_design_workflow
        
        # Quick selection for workflow
        anode_options = ["Graphite", "Silicon", "Tin", "LTO", "Hard Carbon"]
        selected_anode = st.selectbox("Select Anode Material:", anode_options, key="workflow_anode")
        
        if selected_anode:
            workflow['anode_material'] = selected_anode
            st.success(f"Selected: {selected_anode}")
        
        # Electrode design option
        st.markdown("#### Electrode Design")
        st.info("Design the anode electrode composition, porosity, mass loading, and density")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔧 Design Anode Electrode", key="design_anode_electrode", use_container_width=True):
                st.session_state.current_page = 'anode_electrode_design'
                st.rerun()
        
        with col2:
            if st.button("📋 View Material Details", key="view_anode_details", use_container_width=True):
                st.session_state.current_page = 'anode_materials'
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip Electrode Design", key="skip_anode_electrode", use_container_width=True):
                workflow['current_step'] = 6
                st.rerun()
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Cathode Material", key="prev_cathode"):
                workflow['current_step'] = 2
                st.rerun()
        
        with col2:
            if st.button("Next: Select Electrolyte & Separator →", key="next_electrolyte", use_container_width=True):
                workflow['current_step'] = 6
                st.rerun()
    
    def render_electrolyte_separator_selection(self):
        """Render electrolyte and separator selection"""
        st.markdown("### 💧 Select Electrolyte & Separator")
        
        workflow = st.session_state.cell_design_workflow
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Electrolyte")
            electrolyte_options = ["LiPF6 in EC:DMC", "LiPF6 in EC:EMC", "LiTFSI in EC:DMC"]
            selected_electrolyte = st.selectbox("Select Electrolyte:", electrolyte_options, key="workflow_electrolyte")
            workflow['electrolyte'] = selected_electrolyte
        
        with col2:
            st.markdown("#### Separator")
            separator_options = ["PE", "PP", "PE/PP Trilayer"]
            selected_separator = st.selectbox("Select Separator:", separator_options, key="workflow_separator")
            workflow['separator'] = selected_separator
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Anode Electrode", key="prev_anode"):
                workflow['current_step'] = 3
                st.rerun()
        
        with col2:
            if st.button("Next: Select Safety Features →", key="next_safety", use_container_width=True):
                workflow['current_step'] = 5
                st.rerun()
    
    def render_safety_features_selection(self):
        """Render safety features selection"""
        st.markdown("### 🛡️ Select Safety Features")
        
        workflow = st.session_state.cell_design_workflow
        form_factor = workflow.get('form_factor', 'cylindrical')
        
        if form_factor == 'cylindrical':
            st.markdown("#### Cylindrical Cell Safety Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                vent_mechanism = st.checkbox("Vent Mechanism", key="vent_mechanism", value=True)
                cid_device = st.checkbox("CID (Current Interrupt Device)", key="cid_device", value=True)
                ptc_device = st.checkbox("PTC (Positive Temperature Coefficient)", key="ptc_device", value=False)
            
            with col2:
                thermal_fuse = st.checkbox("Thermal Fuse", key="thermal_fuse", value=False)
                pressure_valve = st.checkbox("Pressure Relief Valve", key="pressure_valve", value=True)
                insulation = st.checkbox("Insulation Layer", key="insulation", value=True)
            
            # Store safety features
            workflow['safety_features'] = {
                'vent_mechanism': vent_mechanism,
                'cid_device': cid_device,
                'ptc_device': ptc_device,
                'thermal_fuse': thermal_fuse,
                'pressure_valve': pressure_valve,
                'insulation': insulation
            }
        
        else:
            st.markdown("#### Pouch/Prismatic Cell Safety Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                thermal_fuse = st.checkbox("Thermal Fuse", key="thermal_fuse_pouch", value=True)
                pressure_relief = st.checkbox("Pressure Relief", key="pressure_relief", value=True)
                insulation = st.checkbox("Insulation Layer", key="insulation_pouch", value=True)
            
            with col2:
                overcurrent_protection = st.checkbox("Overcurrent Protection", key="overcurrent_protection", value=True)
                thermal_management = st.checkbox("Thermal Management", key="thermal_management", value=True)
                mechanical_protection = st.checkbox("Mechanical Protection", key="mechanical_protection", value=True)
            
            # Store safety features
            workflow['safety_features'] = {
                'thermal_fuse': thermal_fuse,
                'pressure_relief': pressure_relief,
                'insulation': insulation,
                'overcurrent_protection': overcurrent_protection,
                'thermal_management': thermal_management,
                'mechanical_protection': mechanical_protection
            }
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Electrolyte & Separator", key="prev_electrolyte"):
                workflow['current_step'] = 4
                st.rerun()
        
        with col2:
            if st.button("Next: Run Simulation →", key="next_simulation", use_container_width=True):
                workflow['current_step'] = 6
                st.rerun()
    
    def render_simulation(self):
        """Render simulation page with performance, thermal, and aging simulations"""
        st.markdown("### 🔬 Cell Simulation")
        
        workflow = st.session_state.cell_design_workflow
        
        # Display design summary
        st.markdown("#### Design Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Form Factor", workflow.get('form_factor', 'Not selected').title())
            st.metric("Casing Material", workflow.get('casing_material', 'Not selected'))
        
        with col2:
            st.metric("Cathode", workflow.get('cathode_material', 'Not selected'))
            st.metric("Anode", workflow.get('anode_material', 'Not selected'))
        
        with col3:
            st.metric("Electrolyte", workflow.get('electrolyte', 'Not selected'))
            st.metric("Separator", workflow.get('separator', 'Not selected'))
        
        # Simulation tabs
        tab1, tab2, tab3 = st.tabs(["⚡ Performance", "🌡️ Thermal", "⏰ Aging"])
        
        with tab1:
            self._render_performance_simulation()
        
        with tab2:
            self._render_thermal_simulation()
        
        with tab3:
            self._render_aging_simulation()
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous: Safety Features", key="prev_safety"):
                workflow['current_step'] = 5
                st.rerun()
        
        with col2:
            if st.button("🔄 Restart Workflow", key="restart_workflow", use_container_width=True):
                workflow['current_step'] = 0
                workflow['form_factor'] = None
                workflow['casing_material'] = None
                workflow['cathode_material'] = None
                workflow['anode_material'] = None
                workflow['electrolyte'] = None
                workflow['separator'] = None
                workflow['safety_features'] = {}
                st.rerun()
    
    def _render_performance_simulation(self):
        """Render performance simulation (DCIR, Energy, Power)"""
        st.markdown("#### Performance Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**DCIR Analysis**")
            if st.button("Run DCIR Simulation", key="dcir_sim"):
                # Simulate DCIR results
                st.success("DCIR simulation completed!")
                
                # Create DCIR plot
                soc = np.linspace(0, 100, 100)
                dcir = 0.1 + 0.05 * (soc/100) + 0.02 * np.sin(2 * np.pi * soc/50)
                
                fig = px.line(x=soc, y=dcir, title="DCIR vs State of Charge")
                fig.update_layout(xaxis_title="State of Charge (%)", yaxis_title="DCIR (Ω)")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Energy & Power Analysis**")
            if st.button("Run Energy/Power Simulation", key="energy_power_sim"):
                st.success("Energy/Power simulation completed!")
                
                # Create Ragone plot
                energy_density = np.linspace(100, 300, 50)
                power_density = 1000 * np.exp(-energy_density/200)
                
                fig = px.scatter(x=energy_density, y=power_density, title="Ragone Plot")
                fig.update_layout(xaxis_title="Energy Density (Wh/kg)", yaxis_title="Power Density (W/kg)")
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_thermal_simulation(self):
        """Render thermal simulation with flexible cooling conditions"""
        st.markdown("#### Thermal Simulation")
        
        # Cooling conditions
        st.markdown("**Cooling Conditions**")
        col1, col2 = st.columns(2)
        
        with col1:
            cooling_type = st.selectbox("Cooling Type", ["Natural Convection", "Forced Air", "Liquid Cooling"], key="cooling_type")
            ambient_temp = st.slider("Ambient Temperature (°C)", 20, 50, 25, key="ambient_temp")
        
        with col2:
            heat_transfer_coeff = st.slider("Heat Transfer Coefficient (W/m²·K)", 5, 100, 25, key="htc")
            if cooling_type == "Liquid Cooling":
                coolant_temp = st.slider("Coolant Temperature (°C)", 15, 35, 20, key="coolant_temp")
        
        if st.button("Run Thermal Simulation", key="thermal_sim"):
            st.success("Thermal simulation completed!")
            
            # Create thermal plot
            time = np.linspace(0, 3600, 100)  # 1 hour
            temp = ambient_temp + 20 * (1 - np.exp(-time/600)) + 5 * np.sin(time/300)
            
            fig = px.line(x=time/60, y=temp, title="Temperature vs Time")
            fig.update_layout(xaxis_title="Time (minutes)", yaxis_title="Temperature (°C)")
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_aging_simulation(self):
        """Render aging simulation"""
        st.markdown("#### Aging Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cycles = st.slider("Number of Cycles", 100, 5000, 1000, key="aging_cycles")
            temp_aging = st.slider("Aging Temperature (°C)", 25, 60, 45, key="aging_temp")
        
        with col2:
            soc_range = st.slider("SOC Range (%)", 20, 100, 80, key="soc_range")
            c_rate = st.slider("C-Rate", 0.5, 2.0, 1.0, key="c_rate")
        
        if st.button("Run Aging Simulation", key="aging_sim"):
            st.success("Aging simulation completed!")
            
            # Create aging plot
            cycle_numbers = np.linspace(0, cycles, 100)
            capacity_retention = 100 * np.exp(-cycle_numbers/2000) + 5 * np.sin(cycle_numbers/500)
            
            fig = px.line(x=cycle_numbers, y=capacity_retention, title="Capacity Retention vs Cycles")
            fig.update_layout(xaxis_title="Cycle Number", yaxis_title="Capacity Retention (%)")
            st.plotly_chart(fig, use_container_width=True)
