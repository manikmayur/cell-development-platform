"""
OCV (Open Circuit Voltage) Curves Module
Provides realistic OCV curves for different battery materials
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Optional
from .theme_colors import get_plotly_theme, get_current_theme


class OCVCurveGenerator:
    """Generates realistic OCV curves for different battery materials"""
    
    def __init__(self):
        self.plotly_theme = get_plotly_theme()[get_current_theme()]
        self.material_database = self._load_material_database()
    
    def _load_material_database(self) -> Dict:
        """Load material database from JSON file"""
        try:
            database_path = "data/material_database.json"
            if os.path.exists(database_path):
                with open(database_path, 'r') as f:
                    return json.load(f)
            else:
                st.error(f"Material database not found at {database_path}")
                return {"materials": {}}
        except Exception as e:
            st.error(f"Error loading material database: {e}")
            return {"materials": {}}
    
    def get_available_materials(self) -> List[str]:
        """Get list of available materials from database"""
        return list(self.material_database.get("materials", {}).keys())
    
    def get_material_data(self, material: str) -> Dict:
        """Get material data from database"""
        materials = self.material_database.get("materials", {})
        if material not in materials:
            raise ValueError(f"Material {material} not found in database")
        return materials[material]
    
    def generate_ocv_from_database(self, material: str, temperature: float = 25.0) -> Tuple[np.ndarray, np.ndarray]:
        """Generate OCV curve from material database"""
        
        material_data = self.get_material_data(material)
        ocv_data = material_data['ocv_curve']
        
        # Get capacity and voltage points from database
        capacity_points = np.array(ocv_data['capacity_points'])
        voltage_points = np.array(ocv_data['voltage_points'])
        
        # Create high-resolution interpolation
        capacity_high_res = np.linspace(0, capacity_points[-1], 1000)
        
        # Interpolate voltage points
        voltage_high_res = np.interp(capacity_high_res, capacity_points, voltage_points)
        
        # Temperature correction
        temp_factor = 1 + 0.0001 * (temperature - 25)
        voltage_high_res *= temp_factor
        
        # Add slight noise for realism
        noise = np.random.normal(0, 0.001, len(capacity_high_res))
        voltage_high_res += noise
        
        # Smooth the curve
        try:
            from scipy.ndimage import gaussian_filter1d
            voltage_high_res = gaussian_filter1d(voltage_high_res, sigma=1)
        except ImportError:
            # Fallback to simple smoothing if scipy not available
            voltage_high_res = np.convolve(voltage_high_res, np.ones(3)/3, mode='same')
        
        # Ensure voltage stays within bounds
        voltage_range = material_data['voltage_range']
        voltage_high_res = np.clip(voltage_high_res, voltage_range['min'], voltage_range['max'])
        
        return capacity_high_res, voltage_high_res
    
    def generate_graphite_ocv(self, temperature: float = 25.0) -> Tuple[np.ndarray, np.ndarray]:
        """Generate OCV curve for graphite anode from database"""
        return self.generate_ocv_from_database('graphite', temperature)
    
    def generate_cathode_ocv(self, material: str, temperature: float = 25.0) -> Tuple[np.ndarray, np.ndarray]:
        """Generate OCV curve for cathode materials from database"""
        return self.generate_ocv_from_database(material, temperature)
    
    def plot_ocv_curve(self, material: str, temperature: float = 25.0, 
                      show_plateaus: bool = True, show_derivative: bool = False) -> go.Figure:
        """Plot OCV curve for a material"""
        
        # Get material data from database
        material_data = self.get_material_data(material)
        
        if material == 'graphite':
            capacity, voltage = self.generate_graphite_ocv(temperature)
            title = f"Graphite Anode OCV Curve at {temperature}°C"
            x_label = "Capacity (mAh/g)"
            y_label = "Voltage vs Li/Li+ (V)"
            color = '#e74c3c'  # Red for anode
        else:
            capacity, voltage = self.generate_cathode_ocv(material, temperature)
            title = f"{material_data['name']} Cathode OCV Curve at {temperature}°C"
            x_label = "Capacity (mAh/g)"
            y_label = "Voltage vs Li/Li+ (V)"
            color = '#3498db'  # Blue for cathode
        
        # Create main plot
        fig = go.Figure()
        
        # Add main OCV curve
        fig.add_trace(go.Scatter(
            x=capacity,
            y=voltage,
            mode='lines',
            name='OCV Curve',
            line=dict(color=color, width=3),
            hovertemplate=f'<b>{x_label}</b>: %{{x:.1f}}<br><b>{y_label}</b>: %{{y:.3f}}<extra></extra>'
        ))
        
        # Add plateau regions if requested
        if show_plateaus and 'staging_regions' in material_data['ocv_curve']:
            staging_regions = material_data['ocv_curve']['staging_regions']
            for i, region in enumerate(staging_regions):
                plateau_capacity = np.linspace(region['capacity_range'][0], region['capacity_range'][1], 100)
                plateau_voltage = np.full_like(plateau_capacity, region['voltage_range'][0])
                
                fig.add_trace(go.Scatter(
                    x=plateau_capacity,
                    y=plateau_voltage,
                    mode='lines',
                    name=f"Region {i+1}",
                    line=dict(color=color, width=1, dash='dash'),
                    opacity=0.6,
                    showlegend=False,
                    hovertemplate=f'<b>{region["name"]}</b><br>{region["description"]}<br><b>Voltage Range</b>: {region["voltage_range"][0]:.3f} - {region["voltage_range"][1]:.3f} V<extra></extra>'
                ))
        
        # Add derivative if requested
        if show_derivative:
            # Calculate numerical derivative
            dV_dQ = np.gradient(voltage, capacity)
            
            # Create secondary y-axis for derivative
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=capacity,
                y=dV_dQ,
                mode='lines',
                name='dV/dQ',
                line=dict(color='orange', width=2),
                yaxis='y2',
                hovertemplate=f'<b>{x_label}</b>: %{{x:.1f}}<br><b>dV/dQ</b>: %{{y:.4f}} V/mAh<extra></extra>'
            ))
            
            # Update layout for secondary y-axis
            fig.update_layout(
                yaxis2=dict(
                    title="dV/dQ (V/mAh)",
                    overlaying="y",
                    side="right",
                    color="orange"
                )
            )
            
            # Add derivative trace to main figure
            fig.add_trace(go.Scatter(
                x=capacity,
                y=dV_dQ,
                mode='lines',
                name='dV/dQ',
                line=dict(color='orange', width=2),
                yaxis='y2',
                hovertemplate=f'<b>{x_label}</b>: %{{x:.1f}}<br><b>dV/dQ</b>: %{{y:.4f}} V/mAh<extra></extra>'
            ))
        
        # Update layout
        layout_updates = {
            'title': dict(
                text=title,
                font=dict(size=20, color=self.plotly_theme['layout']['font']['color'])
            ),
            'xaxis': dict(
                title=x_label,
                showgrid=True,
                gridcolor=self.plotly_theme['layout']['xaxis']['gridcolor'],
                linecolor=self.plotly_theme['layout']['xaxis']['linecolor'],
                tickcolor=self.plotly_theme['layout']['xaxis']['tickcolor']
            ),
            'yaxis': dict(
                title=y_label,
                showgrid=True,
                gridcolor=self.plotly_theme['layout']['yaxis']['gridcolor'],
                linecolor=self.plotly_theme['layout']['yaxis']['linecolor'],
                tickcolor=self.plotly_theme['layout']['yaxis']['tickcolor']
            ),
            'hovermode': 'x unified',
            'height': 500,
            'margin': dict(l=60, r=60, t=80, b=60)
        }
        
        # Merge with theme layout, avoiding conflicts
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def plot_comparison(self, materials: List[str], temperature: float = 25.0) -> go.Figure:
        """Plot OCV curves for multiple materials"""
        
        fig = go.Figure()
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for i, material in enumerate(materials):
            if material == 'graphite':
                capacity, voltage = self.generate_graphite_ocv(temperature)
                name = "Graphite (Anode)"
            else:
                capacity, voltage = self.generate_cathode_ocv(material, temperature)
                material_data = self.get_material_data(material)
                name = f"{material_data['name']} (Cathode)"
            
            fig.add_trace(go.Scatter(
                x=capacity,
                y=voltage,
                mode='lines',
                name=name,
                line=dict(color=colors[i % len(colors)], width=3),
                hovertemplate=f'<b>Material</b>: {name}<br><b>Capacity</b>: %{{x:.1f}} mAh/g<br><b>Voltage</b>: %{{y:.3f}} V<extra></extra>'
            ))
        
        layout_updates = {
            'title': dict(
                text=f"OCV Curves Comparison at {temperature}°C",
                font=dict(size=20, color=self.plotly_theme['layout']['font']['color'])
            ),
            'xaxis': dict(
                title="Capacity (mAh/g)",
                showgrid=True,
                gridcolor=self.plotly_theme['layout']['xaxis']['gridcolor'],
                linecolor=self.plotly_theme['layout']['xaxis']['linecolor'],
                tickcolor=self.plotly_theme['layout']['xaxis']['tickcolor']
            ),
            'yaxis': dict(
                title="Voltage vs Li/Li+ (V)",
                showgrid=True,
                gridcolor=self.plotly_theme['layout']['yaxis']['gridcolor'],
                linecolor=self.plotly_theme['layout']['yaxis']['linecolor'],
                tickcolor=self.plotly_theme['layout']['yaxis']['tickcolor']
            ),
            'hovermode': 'x unified',
            'height': 500,
            'margin': dict(l=60, r=60, t=80, b=60)
        }
        
        # Merge with theme layout, avoiding conflicts
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def get_material_properties(self, material: str) -> Dict:
        """Get material properties for OCV curve from database"""
        material_data = self.get_material_data(material)
        
        # Convert database format to expected format
        return {
            'name': material_data['name'],
            'type': material_data['type'],
            'voltage_range': (material_data['voltage_range']['min'], material_data['voltage_range']['max']),
            'capacity_range': (0, material_data['theoretical_capacity']),
            'curve_type': 'database',
            'plateaus': material_data['ocv_curve'].get('staging_regions', [])
        }


def render_ocv_demo():
    """Render OCV curves demo page"""
    
    st.title("🔋 OCV Curves Demo")
    st.markdown("Realistic Open Circuit Voltage curves for battery materials")
    
    # Initialize OCV generator
    ocv_gen = OCVCurveGenerator()
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
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
            "nca": "NCA (Cathode)"
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
        st.markdown("### Material Properties")
        st.write(f"**Name**: {properties['name']}")
        st.write(f"**Type**: {properties['type'].title()}")
        st.write(f"**Voltage Range**: {properties['voltage_range'][0]:.2f} - {properties['voltage_range'][1]:.2f} V")
        st.write(f"**Capacity Range**: 0 - {properties['capacity_range'][1]} mAh/g")
        st.write(f"**Curve Type**: {properties['curve_type'].title()}")
    
    with col2:
        st.markdown("### Key Features")
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
    st.markdown("### OCV Curve")
    fig = ocv_gen.plot_ocv_curve(material, temperature, show_plateaus, show_derivative)
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparison plot
    if st.checkbox("Show Comparison with Other Materials"):
        st.markdown("### Material Comparison")
        comparison_materials = st.multiselect(
            "Select materials to compare:",
            available_materials,
            default=[material, "nmc811"] if material != "nmc811" else [material, "graphite"]
        )
        
        if comparison_materials:
            comp_fig = ocv_gen.plot_comparison(comparison_materials, temperature)
            st.plotly_chart(comp_fig, use_container_width=True)
    
    # Technical details
    st.markdown("### Technical Details")
    
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


if __name__ == "__main__":
    render_ocv_demo()
