"""
Enhanced Schematic Generator for Cell Development Platform
Creates detailed multi-view schematics for different cell form factors
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Tuple, List
from .theme_colors import get_theme_colors, get_plotly_theme, get_current_theme


class SchematicGenerator:
    """Generates detailed schematics for different cell form factors"""
    
    def __init__(self):
        self.colors = get_theme_colors()
        self.plotly_theme = get_plotly_theme()[get_current_theme()]
        
        # Define layer colors for different components
        self.layer_colors = {
            'casing': '#2c3e50',      # Dark blue-gray
            'cathode': '#e74c3c',     # Red
            'anode': '#3498db',       # Blue
            'separator': '#f39c12',   # Orange
            'electrolyte': '#9b59b6', # Purple
            'terminal': '#34495e',    # Dark gray
            'tab': '#95a5a6',         # Light gray
            'interior': '#ecf0f1'     # Very light gray
        }
    
    def create_cylindrical_schematics(self, diameter: float, height: float) -> Tuple[go.Figure, go.Figure]:
        """Create cross-section and side view schematics for cylindrical cell"""
        
        # Calculate scaled dimensions (normalize to reasonable plot size)
        # Use smaller scale factor for cross section to make it bigger
        cross_scale_factor = 30.0  # Smaller scale = bigger cross section
        side_scale_factor = 50.0   # Keep side view scale reasonable
        
        d_cross_scaled = diameter / cross_scale_factor
        d_side_scaled = diameter / side_scale_factor
        h_scaled = height / side_scale_factor
        
        # Cross-section view (top view) - bigger to show inner diameter better
        cross_section = self._create_cylindrical_cross_section(d_cross_scaled)
        
        # Side view
        side_view = self._create_cylindrical_side_view(d_side_scaled, h_scaled)
        
        return cross_section, side_view
    
    def _create_cylindrical_cross_section(self, diameter: float) -> go.Figure:
        """Create cross-section view of cylindrical cell"""
        fig = go.Figure()
        
        # Create concentric circles for different layers
        theta = np.linspace(0, 2*np.pi, 100)
        
        # Outer casing
        r_outer = diameter / 2
        x_outer = r_outer * np.cos(theta)
        y_outer = r_outer * np.sin(theta)
        
        # Cathode layer
        r_cathode = r_outer * 0.9
        x_cathode = r_cathode * np.cos(theta)
        y_cathode = r_cathode * np.sin(theta)
        
        # Separator layer
        r_separator = r_outer * 0.7
        x_separator = r_separator * np.cos(theta)
        y_separator = r_separator * np.sin(theta)
        
        # Anode layer
        r_anode = r_outer * 0.5
        x_anode = r_anode * np.cos(theta)
        y_anode = r_anode * np.sin(theta)
        
        # Center core (electrolyte)
        r_core = r_outer * 0.3
        x_core = r_core * np.cos(theta)
        y_core = r_core * np.sin(theta)
        
        # Add single block for cylindrical cell
        fig.add_trace(go.Scatter(x=x_outer, y=y_outer, fill='toself',
                                fillcolor='#3498db',
                                line=dict(color='#2980b9', width=3),
                                name='Cylindrical Cell'))
        
        # Add inner circle for inner diameter - make it more prominent
        r_inner = r_outer * 0.65  # Make inner diameter larger for better visibility
        x_inner = r_inner * np.cos(theta)
        y_inner = r_inner * np.sin(theta)
        
        fig.add_trace(go.Scatter(x=x_inner, y=y_inner, fill='toself',
                                fillcolor='rgba(52, 152, 219, 0.2)',
                                line=dict(color='#e74c3c', width=3, dash='dash'),  # Red dashed line for better visibility
                                name='Inner Diameter'))
        
        # Add outer diameter annotation
        fig.add_annotation(x=0, y=r_outer + 0.15, text="D (Outer)", showarrow=True, 
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=12, color="red"))
        
        # Add inner diameter annotation - make it more visible
        fig.add_annotation(x=0, y=r_inner + 0.15, text="d (Inner)", showarrow=True, 
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=14, color="red", family="Arial Black"))
        
        # Add center point
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', 
                                marker=dict(size=4, color='black'),
                                name='Center'))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Cylindrical Cell - Cross Section View",
            'xaxis': dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False, showticklabels=False,
                         range=[-r_outer-0.3, r_outer+0.3]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-r_outer-0.3, r_outer+0.3]),
            'showlegend': False,
            'height': 500,
            'margin': dict(l=20, r=20, t=40, b=20)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def _create_cylindrical_side_view(self, diameter: float, height: float) -> go.Figure:
        """Create side view of cylindrical cell"""
        fig = go.Figure()
        
        # Create rectangular layers for side view
        d_half = diameter / 2
        
        # Outer casing
        x_casing = [-d_half, d_half, d_half, -d_half, -d_half]
        y_casing = [0, 0, height, height, 0]
        
        # Cathode layer
        d_cathode = d_half * 0.9
        x_cathode = [-d_cathode, d_cathode, d_cathode, -d_cathode, -d_cathode]
        y_cathode = [0, 0, height, height, 0]
        
        # Separator layer
        d_separator = d_half * 0.7
        x_separator = [-d_separator, d_separator, d_separator, -d_separator, -d_separator]
        y_separator = [0, 0, height, height, 0]
        
        # Anode layer
        d_anode = d_half * 0.5
        x_anode = [-d_anode, d_anode, d_anode, -d_anode, -d_anode]
        y_anode = [0, 0, height, height, 0]
        
        # Center core
        d_core = d_half * 0.3
        x_core = [-d_core, d_core, d_core, -d_core, -d_core]
        y_core = [0, 0, height, height, 0]
        
        # Add single block for cylindrical cell
        fig.add_trace(go.Scatter(x=x_casing, y=y_casing, fill='toself',
                                fillcolor='#3498db',
                                line=dict(color='#2980b9', width=3),
                                name='Cylindrical Cell'))
        
        # Add terminal on top
        terminal_width = d_half * 0.3
        terminal_height = height * 0.05
        x_terminal = [-terminal_width/2, terminal_width/2, terminal_width/2, -terminal_width/2, -terminal_width/2]
        y_terminal = [height, height, height + terminal_height, height + terminal_height, height]
        
        fig.add_trace(go.Scatter(x=x_terminal, y=y_terminal, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal'))
        
        # Add dimension annotations
        fig.add_annotation(x=0, y=height + terminal_height + 0.1, text="H", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=14, color="red"))
        
        fig.add_annotation(x=d_half + 0.1, y=height/2, text="D", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Cylindrical Cell - Side View",
            'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-d_half-0.2, d_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-0.2, height+terminal_height+0.2]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=20, r=20, t=40, b=20)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def create_pouch_schematics(self, height: float, width: float, length: float) -> Tuple[go.Figure, go.Figure]:
        """Create front and side view schematics for pouch cell with top terminals"""
        
        # Calculate scaled dimensions
        scale_factor = 100.0
        h_scaled = height / scale_factor
        w_scaled = width / scale_factor
        l_scaled = length / scale_factor
        
        # Front view
        front_view = self._create_pouch_front_view(h_scaled, w_scaled, l_scaled)
        
        # Side view
        side_view = self._create_pouch_side_view(h_scaled, w_scaled, l_scaled)
        
        return front_view, side_view
    
    def _create_pouch_front_view(self, height: float, width: float, length: float) -> go.Figure:
        """Create front view of pouch cell with top terminals"""
        fig = go.Figure()
        
        # Main pouch body
        w_half = width / 2
        h_half = height / 2
        
        # Pouch outline
        x_pouch = [-w_half, w_half, w_half, -w_half, -w_half]
        y_pouch = [-h_half, -h_half, h_half, h_half, -h_half]
        
        # Top terminals
        terminal_width = w_half * 0.3
        terminal_height = h_half * 0.1
        
        # Closely spaced terminals
        terminal_width = w_half * 0.15
        terminal_spacing = w_half * 0.1  # Close spacing
        
        # Positive terminal (left)
        x_term_pos = [-w_half*0.2 - terminal_width/2, -w_half*0.2 + terminal_width/2, 
                     -w_half*0.2 + terminal_width/2, -w_half*0.2 - terminal_width/2, -w_half*0.2 - terminal_width/2]
        y_term_pos = [h_half, h_half, h_half + terminal_height, h_half + terminal_height, h_half]
        
        # Negative terminal (right, close to positive)
        x_term_neg = [w_half*0.2 - terminal_width/2, w_half*0.2 + terminal_width/2, 
                     w_half*0.2 + terminal_width/2, w_half*0.2 - terminal_width/2, w_half*0.2 - terminal_width/2]
        y_term_neg = [h_half, h_half, h_half + terminal_height, h_half + terminal_height, h_half]
        
        # Internal layers (simplified for front view)
        layer_spacing = h_half * 0.15
        
        # Cathode layer
        x_cathode = [-w_half*0.8, w_half*0.8, w_half*0.8, -w_half*0.8, -w_half*0.8]
        y_cathode = [-h_half*0.8, -h_half*0.8, h_half*0.8, h_half*0.8, -h_half*0.8]
        
        # Separator layer
        x_separator = [-w_half*0.6, w_half*0.6, w_half*0.6, -w_half*0.6, -w_half*0.6]
        y_separator = [-h_half*0.6, -h_half*0.6, h_half*0.6, h_half*0.6, -h_half*0.6]
        
        # Anode layer
        x_anode = [-w_half*0.4, w_half*0.4, w_half*0.4, -w_half*0.4, -w_half*0.4]
        y_anode = [-h_half*0.4, -h_half*0.4, h_half*0.4, h_half*0.4, -h_half*0.4]
        
        # Add single block for pouch cell
        fig.add_trace(go.Scatter(x=x_pouch, y=y_pouch, fill='toself',
                                fillcolor='#e74c3c',
                                line=dict(color='#c0392b', width=3),
                                name='Pouch Cell'))
        
        # Add terminals
        fig.add_trace(go.Scatter(x=x_term_pos, y=y_term_pos, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal +'))
        
        fig.add_trace(go.Scatter(x=x_term_neg, y=y_term_neg, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal -'))
        
        # Add dimension annotations
        fig.add_annotation(x=0, y=h_half + 0.2, text="H", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=14, color="red"))
        
        fig.add_annotation(x=w_half + 0.1, y=0, text="W", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Pouch Cell - Front View (with Top Terminals)",
            'xaxis': dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False, showticklabels=False,
                         range=[-w_half-0.2, w_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=20, r=20, t=40, b=20)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def _create_pouch_side_view(self, height: float, width: float, length: float) -> go.Figure:
        """Create side view of pouch cell"""
        fig = go.Figure()
        
        # Main pouch body (side view shows thickness)
        h_half = height / 2
        l_half = length / 2
        
        # Pouch outline
        x_pouch = [-l_half, l_half, l_half, -l_half, -l_half]
        y_pouch = [-h_half, -h_half, h_half, h_half, -h_half]
        
        # Top terminals (side view)
        terminal_length = l_half * 0.4
        terminal_height = h_half * 0.1
        
        # Positive terminal
        x_term_pos = [-l_half*0.2, l_half*0.2, l_half*0.2, -l_half*0.2, -l_half*0.2]
        y_term_pos = [h_half, h_half, h_half + terminal_height, h_half + terminal_height, h_half]
        
        # Internal layers (side view)
        layer_spacing = l_half * 0.1
        
        # Cathode layer
        x_cathode = [-l_half*0.8, l_half*0.8, l_half*0.8, -l_half*0.8, -l_half*0.8]
        y_cathode = [-h_half*0.8, -h_half*0.8, h_half*0.8, h_half*0.8, -h_half*0.8]
        
        # Separator layer
        x_separator = [-l_half*0.6, l_half*0.6, l_half*0.6, -l_half*0.6, -l_half*0.6]
        y_separator = [-h_half*0.6, -h_half*0.6, h_half*0.6, h_half*0.6, -h_half*0.6]
        
        # Anode layer
        x_anode = [-l_half*0.4, l_half*0.4, l_half*0.4, -l_half*0.4, -l_half*0.4]
        y_anode = [-h_half*0.4, -h_half*0.4, h_half*0.4, h_half*0.4, -h_half*0.4]
        
        # Add single block for pouch cell
        fig.add_trace(go.Scatter(x=x_pouch, y=y_pouch, fill='toself',
                                fillcolor='#e74c3c',
                                line=dict(color='#c0392b', width=3),
                                name='Pouch Cell'))
        
        # Add terminal
        fig.add_trace(go.Scatter(x=x_term_pos, y=y_term_pos, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal'))
        
        # Add dimension annotations
        fig.add_annotation(x=0, y=h_half + 0.2, text="H", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=14, color="red"))
        
        fig.add_annotation(x=l_half + 0.1, y=0, text="L", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Pouch Cell - Side View",
            'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-l_half-0.2, l_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=20, r=20, t=40, b=20)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def create_prismatic_schematics(self, height: float, width: float, length: float) -> Tuple[go.Figure, go.Figure]:
        """Create front and side view schematics for prismatic cell with top terminals"""
        
        # Calculate scaled dimensions
        scale_factor = 100.0
        h_scaled = height / scale_factor
        w_scaled = width / scale_factor
        l_scaled = length / scale_factor
        
        # Front view
        front_view = self._create_prismatic_front_view(h_scaled, w_scaled, l_scaled)
        
        # Side view
        side_view = self._create_prismatic_side_view(h_scaled, w_scaled, l_scaled)
        
        return front_view, side_view
    
    def _create_prismatic_front_view(self, height: float, width: float, length: float) -> go.Figure:
        """Create front view of prismatic cell with top terminals"""
        fig = go.Figure()
        
        # Main prismatic body
        w_half = width / 2
        h_half = height / 2
        
        # Prismatic outline
        x_prism = [-w_half, w_half, w_half, -w_half, -w_half]
        y_prism = [-h_half, -h_half, h_half, h_half, -h_half]
        
        # Top terminals
        terminal_width = w_half * 0.2
        terminal_height = h_half * 0.15
        
        # Widely spaced terminals
        terminal_width = w_half * 0.2
        
        # Positive terminal (far left)
        x_term_pos = [-w_half*0.7, -w_half*0.5, -w_half*0.5, -w_half*0.7, -w_half*0.7]
        y_term_pos = [h_half, h_half, h_half + terminal_height, h_half + terminal_height, h_half]
        
        # Negative terminal (far right)
        x_term_neg = [w_half*0.5, w_half*0.7, w_half*0.7, w_half*0.5, w_half*0.5]
        y_term_neg = [h_half, h_half, h_half + terminal_height, h_half + terminal_height, h_half]
        
        # Internal layers
        # Cathode layer
        x_cathode = [-w_half*0.8, w_half*0.8, w_half*0.8, -w_half*0.8, -w_half*0.8]
        y_cathode = [-h_half*0.8, -h_half*0.8, h_half*0.8, h_half*0.8, -h_half*0.8]
        
        # Separator layer
        x_separator = [-w_half*0.6, w_half*0.6, w_half*0.6, -w_half*0.6, -w_half*0.6]
        y_separator = [-h_half*0.6, -h_half*0.6, h_half*0.6, h_half*0.6, -h_half*0.6]
        
        # Anode layer
        x_anode = [-w_half*0.4, w_half*0.4, w_half*0.4, -w_half*0.4, -w_half*0.4]
        y_anode = [-h_half*0.4, -h_half*0.4, h_half*0.4, h_half*0.4, -h_half*0.4]
        
        # Add single block for prismatic cell
        fig.add_trace(go.Scatter(x=x_prism, y=y_prism, fill='toself',
                                fillcolor='#27ae60',
                                line=dict(color='#229954', width=3),
                                name='Prismatic Cell'))
        
        # Add terminals
        fig.add_trace(go.Scatter(x=x_term_pos, y=y_term_pos, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal +'))
        
        fig.add_trace(go.Scatter(x=x_term_neg, y=y_term_neg, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal -'))
        
        # Add dimension annotations
        fig.add_annotation(x=0, y=h_half + 0.2, text="H", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=14, color="red"))
        
        fig.add_annotation(x=w_half + 0.1, y=0, text="W", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Prismatic Cell - Front View (with Top Terminals)",
            'xaxis': dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False, showticklabels=False,
                         range=[-w_half-0.2, w_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=20, r=20, t=40, b=20)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def _create_prismatic_side_view(self, height: float, width: float, length: float) -> go.Figure:
        """Create side view of prismatic cell"""
        fig = go.Figure()
        
        # Main prismatic body (side view shows thickness)
        h_half = height / 2
        l_half = length / 2
        
        # Prismatic outline
        x_prism = [-l_half, l_half, l_half, -l_half, -l_half]
        y_prism = [-h_half, -h_half, h_half, h_half, -h_half]
        
        # Top terminals (side view)
        terminal_length = l_half * 0.3
        terminal_height = h_half * 0.15
        
        # Positive terminal
        x_term_pos = [-l_half*0.15, l_half*0.15, l_half*0.15, -l_half*0.15, -l_half*0.15]
        y_term_pos = [h_half, h_half, h_half + terminal_height, h_half + terminal_height, h_half]
        
        # Internal layers (side view)
        # Cathode layer
        x_cathode = [-l_half*0.8, l_half*0.8, l_half*0.8, -l_half*0.8, -l_half*0.8]
        y_cathode = [-h_half*0.8, -h_half*0.8, h_half*0.8, h_half*0.8, -h_half*0.8]
        
        # Separator layer
        x_separator = [-l_half*0.6, l_half*0.6, l_half*0.6, -l_half*0.6, -l_half*0.6]
        y_separator = [-h_half*0.6, -h_half*0.6, h_half*0.6, h_half*0.6, -h_half*0.6]
        
        # Anode layer
        x_anode = [-l_half*0.4, l_half*0.4, l_half*0.4, -l_half*0.4, -l_half*0.4]
        y_anode = [-h_half*0.4, -h_half*0.4, h_half*0.4, h_half*0.4, -h_half*0.4]
        
        # Add single block for prismatic cell
        fig.add_trace(go.Scatter(x=x_prism, y=y_prism, fill='toself',
                                fillcolor='#27ae60',
                                line=dict(color='#229954', width=3),
                                name='Prismatic Cell'))
        
        # Add terminal
        fig.add_trace(go.Scatter(x=x_term_pos, y=y_term_pos, fill='toself',
                                fillcolor='#f39c12',
                                line=dict(color='#e67e22', width=2),
                                name='Terminal'))
        
        # Add dimension annotations
        fig.add_annotation(x=0, y=h_half + 0.2, text="H", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=14, color="red"))
        
        fig.add_annotation(x=l_half + 0.1, y=0, text="L", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Prismatic Cell - Side View",
            'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-l_half-0.2, l_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=20, r=20, t=40, b=20)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def render_schematics(self, form_factor: str, dimensions: Dict[str, float]):
        """Render appropriate schematics based on form factor"""
        
        # Set consistent height for all charts
        chart_height = 300
        
        if form_factor == "cylindrical":
            diameter = dimensions.get('diameter', 18.0)
            height = dimensions.get('height', 65.0)
            
            st.markdown("### Cylindrical Cell Schematics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cross_section, side_view = self.create_cylindrical_schematics(diameter, height)
                # Set height for cross section (bigger)
                cross_section.update_layout(height=chart_height + 50)
                st.plotly_chart(cross_section, use_container_width=True)
            
            with col2:
                side_view.update_layout(height=chart_height)
                st.plotly_chart(side_view, use_container_width=True)
        
        elif form_factor == "pouch":
            height = dimensions.get('height', 100.0)
            width = dimensions.get('width', 60.0)
            length = dimensions.get('length', 5.0)
            
            st.markdown("### Pouch Cell Schematics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                front_view, side_view = self.create_pouch_schematics(height, width, length)
                # Set consistent height for both views
                front_view.update_layout(height=chart_height)
                st.plotly_chart(front_view, use_container_width=True)
            
            with col2:
                side_view.update_layout(height=chart_height)
                st.plotly_chart(side_view, use_container_width=True)
        
        elif form_factor == "prismatic":
            height = dimensions.get('height', 100.0)
            width = dimensions.get('width', 60.0)
            length = dimensions.get('length', 20.0)
            
            st.markdown("### Prismatic Cell Schematics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                front_view, side_view = self.create_prismatic_schematics(height, width, length)
                # Set consistent height for both views
                front_view.update_layout(height=chart_height)
                st.plotly_chart(front_view, use_container_width=True)
            
            with col2:
                side_view.update_layout(height=chart_height)
                st.plotly_chart(side_view, use_container_width=True)
