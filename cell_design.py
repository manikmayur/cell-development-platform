"""
Cell Design Module for the Cell Development Platform
Handles form factor selection, electrode configuration, and simulation
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional


class CellDesignManager:
    """Manages cell design process and configurations"""
    
    def __init__(self):
        self.form_factors = {
            "cylindrical": {
                "name": "Cylindrical",
                "description": "Standard cylindrical cell (18650, 21700, etc.)",
                "parameters": {"diameter": 18, "height": 65},
                "image": "🔋"
            },
            "pouch": {
                "name": "Pouch",
                "description": "Flexible pouch cell with tabs",
                "parameters": {"height": 100, "width": 60, "length": 5},
                "image": "📱"
            },
            "prismatic": {
                "name": "Prismatic",
                "description": "Rectangular prismatic cell",
                "parameters": {"height": 100, "width": 60, "length": 20},
                "image": "📦"
            }
        }
        
        self.electrode_materials = {
            "cathode": {
                "NMC811": {"capacity": 200, "voltage": 3.8, "density": 4.7},
                "LCO": {"capacity": 140, "voltage": 3.9, "density": 5.1},
                "NCA": {"capacity": 190, "voltage": 3.7, "density": 4.6}
            },
            "anode": {
                "Graphite": {"capacity": 372, "voltage": 0.1, "density": 2.2},
                "Silicon": {"capacity": 4200, "voltage": 0.4, "density": 2.3},
                "Tin": {"capacity": 994, "voltage": 0.6, "density": 7.3}
            }
        }
        
        self.electrolyte_options = {
            "LiPF6_EC_DMC": {
                "name": "LiPF6 in EC:DMC (1:1)",
                "conductivity": 10.0,
                "stability": "High",
                "cost": "Medium"
            },
            "LiPF6_EC_EMC": {
                "name": "LiPF6 in EC:EMC (3:7)",
                "conductivity": 8.5,
                "stability": "High",
                "cost": "Medium"
            },
            "LiTFSI_EC_DMC": {
                "name": "LiTFSI in EC:DMC (1:1)",
                "conductivity": 7.2,
                "stability": "Very High",
                "cost": "High"
            }
        }
        
        self.separator_options = {
            "PE": {
                "name": "Polyethylene (PE)",
                "thickness": 20,
                "porosity": 40,
                "thermal_stability": "Good"
            },
            "PP": {
                "name": "Polypropylene (PP)",
                "thickness": 25,
                "porosity": 35,
                "thermal_stability": "Excellent"
            },
            "PE_PP": {
                "name": "PE/PP Trilayer",
                "thickness": 20,
                "porosity": 40,
                "thermal_stability": "Excellent"
            }
        }
    
    def render_form_factor_selection(self):
        """Render interactive form factor selection"""
        try:
            st.markdown("### 🔋 Select Form Factor")
            st.markdown("Choose the cell form factor and adjust dimensions:")
            
            # Initialize session state for form factor
            if 'selected_form_factor' not in st.session_state:
                st.session_state.selected_form_factor = None
            
            # Create three columns for form factors
            col1, col2, col3 = st.columns(3)
            
            with col1:
                self._render_form_factor_card("cylindrical", col1)
            
            with col2:
                self._render_form_factor_card("pouch", col2)
            
            with col3:
                self._render_form_factor_card("prismatic", col3)
            
            # Show selected form factor details
            if st.session_state.selected_form_factor:
                self._render_form_factor_details()
                
        except Exception as e:
            st.error(f"Error in form factor selection: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    def _render_form_factor_card(self, form_factor_key: str, column):
        """Render individual form factor card"""
        form_factor = self.form_factors[form_factor_key]
        is_selected = st.session_state.selected_form_factor == form_factor_key
        
        # Card styling
        if is_selected:
            card_style = """
            <div style="
                border: 3px solid #1f77b4;
                border-radius: 15px;
                padding: 20px;
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3);
            ">
            """
        else:
            card_style = """
            <div style="
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 20px;
                background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                opacity: 0.7;
            ">
            """
        
        # Card content
        card_content = f"""
        {card_style}
            <div style="font-size: 4rem; margin-bottom: 10px;">{form_factor['image']}</div>
            <h3 style="margin: 10px 0; color: #333;">{form_factor['name']}</h3>
            <p style="color: #666; font-size: 0.9rem;">{form_factor['description']}</p>
        </div>
        """
        
        column.markdown(card_content, unsafe_allow_html=True)
        
        # Selection button
        if column.button(f"Select {form_factor['name']}", key=f"select_{form_factor_key}", use_container_width=True):
            st.session_state.selected_form_factor = form_factor_key
            st.rerun()
    
    def _render_form_factor_details(self):
        """Render detailed form factor configuration"""
        form_factor_key = st.session_state.selected_form_factor
        form_factor = self.form_factors[form_factor_key]
        
        st.markdown(f"#### {form_factor['name']} Configuration")
        
        # Initialize parameters in session state
        param_key = f"form_factor_params_{form_factor_key}"
        if param_key not in st.session_state:
            st.session_state[param_key] = form_factor['parameters'].copy()
        
        # Create columns for parameters and visualization
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Dimensions:**")
            
            if form_factor_key == "cylindrical":
                # Cylindrical parameters
                diameter = st.slider(
                    "Diameter (mm)",
                    min_value=10.0,
                    max_value=50.0,
                    value=float(st.session_state[param_key]["diameter"]),
                    step=0.5,
                    key=f"diameter_{form_factor_key}"
                )
                height = st.slider(
                    "Height (mm)",
                    min_value=30.0,
                    max_value=150.0,
                    value=float(st.session_state[param_key]["height"]),
                    step=1.0,
                    key=f"height_{form_factor_key}"
                )
                
                # Update session state
                st.session_state[param_key]["diameter"] = diameter
                st.session_state[param_key]["height"] = height
                
                # Calculate volume
                volume = np.pi * (diameter/2)**2 * height / 1000  # cm³
                st.metric("Volume", f"{volume:.2f} cm³")
                
            else:  # Pouch and Prismatic
                height = st.slider(
                    "Height (mm)",
                    min_value=50.0,
                    max_value=200.0,
                    value=float(st.session_state[param_key]["height"]),
                    step=1.0,
                    key=f"height_{form_factor_key}"
                )
                width = st.slider(
                    "Width (mm)",
                    min_value=30.0,
                    max_value=150.0,
                    value=float(st.session_state[param_key]["width"]),
                    step=1.0,
                    key=f"width_{form_factor_key}"
                )
                length = st.slider(
                    "Length/Thickness (mm)",
                    min_value=2.0,
                    max_value=50.0,
                    value=float(st.session_state[param_key]["length"]),
                    step=0.5,
                    key=f"length_{form_factor_key}"
                )
                
                # Update session state
                st.session_state[param_key]["height"] = height
                st.session_state[param_key]["width"] = width
                st.session_state[param_key]["length"] = length
                
                # Calculate volume
                volume = height * width * length / 1000  # cm³
                st.metric("Volume", f"{volume:.2f} cm³")
        
        with col2:
            # 3D visualization
            self._render_3d_visualization(form_factor_key)
    
    def _render_3d_visualization(self, form_factor_key: str):
        """Render 3D visualization of the selected form factor"""
        param_key = f"form_factor_params_{form_factor_key}"
        params = st.session_state[param_key]
        
        if form_factor_key == "cylindrical":
            # Create cylindrical visualization
            fig = go.Figure()
            
            # Create cylinder surface
            theta = np.linspace(0, 2*np.pi, 50)
            z = np.linspace(0, params["height"], 20)
            theta_grid, z_grid = np.meshgrid(theta, z)
            x = (params["diameter"]/2) * np.cos(theta_grid)
            y = (params["diameter"]/2) * np.sin(theta_grid)
            
            fig.add_trace(go.Surface(
                x=x, y=y, z=z_grid,
                colorscale='Blues',
                opacity=0.8,
                name='Cylinder'
            ))
            
            fig.update_layout(
                title=f"Cylindrical Cell ({params['diameter']:.1f}mm × {params['height']:.1f}mm)",
                scene=dict(
                    xaxis_title="X (mm)",
                    yaxis_title="Y (mm)",
                    zaxis_title="Height (mm)",
                    aspectmode='data'
                ),
                height=400
            )
            
        else:  # Pouch and Prismatic
            # Create rectangular visualization
            fig = go.Figure()
            
            # Create box vertices
            h, w, l = params["height"], params["width"], params["length"]
            vertices = np.array([
                [0, 0, 0], [l, 0, 0], [l, w, 0], [0, w, 0],  # Bottom
                [0, 0, h], [l, 0, h], [l, w, h], [0, w, h]   # Top
            ])
            
            # Define faces
            faces = [
                [0, 1, 2, 3],  # Bottom
                [4, 5, 6, 7],  # Top
                [0, 1, 5, 4],  # Front
                [2, 3, 7, 6],  # Back
                [0, 3, 7, 4],  # Left
                [1, 2, 6, 5]   # Right
            ]
            
            # Add mesh
            fig.add_trace(go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=[face[0] for face in faces],
                j=[face[1] for face in faces],
                k=[face[2] for face in faces],
                color='lightblue',
                opacity=0.8,
                name=form_factor_key.title()
            ))
            
            fig.update_layout(
                title=f"{form_factor_key.title()} Cell ({h:.1f}×{w:.1f}×{l:.1f}mm)",
                scene=dict(
                    xaxis_title="Length (mm)",
                    yaxis_title="Width (mm)",
                    zaxis_title="Height (mm)",
                    aspectmode='data'
                ),
                height=400
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_electrode_selection(self):
        """Render electrode material selection"""
        if not st.session_state.selected_form_factor:
            st.warning("Please select a form factor first.")
            return
        
        st.markdown("### ⚡ Select Electrodes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Cathode Material")
            cathode_material = st.selectbox(
                "Select Cathode:",
                options=list(self.electrode_materials["cathode"].keys()),
                key="cathode_selection"
            )
            
            # Display cathode properties
            cathode_props = self.electrode_materials["cathode"][cathode_material]
            st.markdown("**Properties:**")
            st.write(f"• Capacity: {cathode_props['capacity']} mAh/g")
            st.write(f"• Voltage: {cathode_props['voltage']} V")
            st.write(f"• Density: {cathode_props['density']} g/cm³")
        
        with col2:
            st.markdown("#### Anode Material")
            anode_material = st.selectbox(
                "Select Anode:",
                options=list(self.electrode_materials["anode"].keys()),
                key="anode_selection"
            )
            
            # Display anode properties
            anode_props = self.electrode_materials["anode"][anode_material]
            st.markdown("**Properties:**")
            st.write(f"• Capacity: {anode_props['capacity']} mAh/g")
            st.write(f"• Voltage: {anode_props['voltage']} V")
            st.write(f"• Density: {anode_props['density']} g/cm³")
        
        # Store selections
        st.session_state.selected_cathode = cathode_material
        st.session_state.selected_anode = anode_material
    
    def render_electrolyte_separator_selection(self):
        """Render electrolyte and separator selection"""
        if not st.session_state.selected_form_factor:
            st.warning("Please select a form factor first.")
            return
        
        st.markdown("### 💧 Select Electrolyte & Separator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Electrolyte")
            electrolyte = st.selectbox(
                "Select Electrolyte:",
                options=list(self.electrolyte_options.keys()),
                key="electrolyte_selection"
            )
            
            # Display electrolyte properties
            electrolyte_props = self.electrolyte_options[electrolyte]
            st.markdown("**Properties:**")
            st.write(f"• Name: {electrolyte_props['name']}")
            st.write(f"• Conductivity: {electrolyte_props['conductivity']} mS/cm")
            st.write(f"• Stability: {electrolyte_props['stability']}")
            st.write(f"• Cost: {electrolyte_props['cost']}")
        
        with col2:
            st.markdown("#### Separator")
            separator = st.selectbox(
                "Select Separator:",
                options=list(self.separator_options.keys()),
                key="separator_selection"
            )
            
            # Display separator properties
            separator_props = self.separator_options[separator]
            st.markdown("**Properties:**")
            st.write(f"• Name: {separator_props['name']}")
            st.write(f"• Thickness: {separator_props['thickness']} μm")
            st.write(f"• Porosity: {separator_props['porosity']}%")
            st.write(f"• Thermal Stability: {separator_props['thermal_stability']}")
        
        # Store selections
        st.session_state.selected_electrolyte = electrolyte
        st.session_state.selected_separator = separator
    
    def render_simulation(self):
        """Render performance and life simulation"""
        if not all([
            st.session_state.get('selected_form_factor'),
            st.session_state.get('selected_cathode'),
            st.session_state.get('selected_anode'),
            st.session_state.get('selected_electrolyte'),
            st.session_state.get('selected_separator')
        ]):
            st.warning("Please complete all selections before running simulation.")
            return
        
        st.markdown("### 🔬 Simulate Performance & Life")
        
        if st.button("🚀 Run Simulation", key="run_simulation", use_container_width=True):
            self._run_simulation()
    
    def _run_simulation(self):
        """Run cell performance and life simulation"""
        # Get cell configuration
        form_factor = st.session_state.selected_form_factor
        cathode = st.session_state.selected_cathode
        anode = st.session_state.selected_anode
        electrolyte = st.session_state.selected_electrolyte
        separator = st.session_state.selected_separator
        
        # Get form factor parameters
        param_key = f"form_factor_params_{form_factor}"
        params = st.session_state[param_key]
        
        # Calculate cell capacity
        cathode_props = self.electrode_materials["cathode"][cathode]
        anode_props = self.electrode_materials["anode"][anode]
        
        # Calculate volume and estimate capacity
        if form_factor == "cylindrical":
            volume = np.pi * (params["diameter"]/2)**2 * params["height"] / 1000  # cm³
        else:
            volume = params["height"] * params["width"] * params["length"] / 1000  # cm³
        
        # Estimate capacity (simplified calculation)
        estimated_capacity = volume * 0.3 * min(cathode_props["capacity"], anode_props["capacity"]) / 1000  # Ah
        
        # Create simulation results
        st.success("✅ Simulation completed!")
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Estimated Capacity", f"{estimated_capacity:.2f} Ah")
        
        with col2:
            st.metric("Energy Density", f"{estimated_capacity * 3.7:.1f} Wh")
        
        with col3:
            st.metric("Cycle Life", "1000+ cycles")
        
        # Performance plots
        self._render_performance_plots(estimated_capacity)
    
    def _render_performance_plots(self, capacity: float):
        """Render performance simulation plots"""
        st.markdown("#### Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Voltage vs Capacity curve
            soc = np.linspace(0, 100, 100)
            voltage = 3.7 - 0.5 * (soc/100) + 0.2 * np.sin(2 * np.pi * soc/100)
            
            fig1 = px.line(
                x=soc,
                y=voltage,
                title="Voltage vs State of Charge",
                labels={'x': 'State of Charge (%)', 'y': 'Voltage (V)'}
            )
            fig1.update_layout(height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Cycle life degradation
            cycles = np.linspace(0, 1000, 100)
            capacity_retention = 100 * np.exp(-cycles/2000)
            
            fig2 = px.line(
                x=cycles,
                y=capacity_retention,
                title="Capacity Retention vs Cycles",
                labels={'x': 'Cycles', 'y': 'Capacity Retention (%)'}
            )
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Cell configuration summary
        st.markdown("#### Cell Configuration Summary")
        config_data = {
            "Parameter": ["Form Factor", "Cathode", "Anode", "Electrolyte", "Separator", "Estimated Capacity"],
            "Value": [
                st.session_state.selected_form_factor.title(),
                st.session_state.selected_cathode,
                st.session_state.selected_anode,
                self.electrolyte_options[st.session_state.selected_electrolyte]["name"],
                self.separator_options[st.session_state.selected_separator]["name"],
                f"{capacity:.2f} Ah"
            ]
        }
        
        config_df = pd.DataFrame(config_data)
        st.dataframe(config_df, use_container_width=True, hide_index=True)
