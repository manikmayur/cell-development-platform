"""
Enhanced Schematic Generator for Cell Development Platform

This module generates high-quality 2D schematics for battery cell form factors.
Supports multiple views and detailed component visualization.

Features:
- Multi-view schematics (cross-section, side view, front view)
- Support for cylindrical, pouch, and prismatic cell types
- Interactive dimension annotations
- Realistic component layering and proportions
- Theme-aware color schemes
- Scalable vector graphics with Plotly

Cell Types Supported:
- Cylindrical: Cross-section and side views with inner/outer diameter
- Pouch: Front and side views with terminal positioning
- Prismatic: Front and side views with terminal configuration

Author: Cell Development Platform Team
Version: 2.0 - Enhanced multi-view support
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Tuple, List
from .theme_colors import get_theme_colors, get_plotly_theme, get_current_theme


class SchematicGenerator:
    """
    Advanced Schematic Generator for Battery Cell Form Factors
    
    This class generates detailed, accurate 2D schematics for various battery cell
    form factors with multi-view support and professional presentation.
    
    Features:
    - Multi-view schematic generation (cross-section, side, front views)
    - Support for cylindrical, pouch, and prismatic cell types
    - Interactive dimension annotations and measurements
    - Realistic component layering with proper proportions
    - Theme-aware color schemes and professional styling
    - Scalable vector graphics using Plotly for high quality output
    
    Supported Cell Types:
    - Cylindrical: Detailed cross-section showing internal layers, side view with dimensions
    - Pouch: Front view with terminal layout, side view showing thickness profile
    - Prismatic: Front and side views with terminal configurations and housing details
    
    The generator creates publication-ready schematics suitable for technical
    documentation, presentations, and manufacturing specifications.
    
    Attributes:
        colors (dict): Theme-aware colors from the color scheme manager
        plotly_theme (dict): Plotly theme configuration for consistent styling
        layer_colors (dict): Predefined colors for different cell components
    
    Methods:
        create_cylindrical_schematics(): Creates cross-section and side view for cylindrical cells
        create_pouch_schematics(): Creates front and side views for pouch cells
        create_prismatic_schematics(): Creates front and side views for prismatic cells
        _create_cylindrical_cross_section(): Internal method for cylindrical cross-section view
        _create_cylindrical_side_view(): Internal method for cylindrical side view
        _create_pouch_front_view(): Internal method for pouch front view
        _create_pouch_side_view(): Internal method for pouch side view
        _create_prismatic_front_view(): Internal method for prismatic front view
        _create_prismatic_side_view(): Internal method for prismatic side view
    """
    
    def __init__(self):
        """
        Initialize the Schematic Generator with theme-aware styling.
        
        Sets up the generator with current theme colors and Plotly configuration
        for consistent, professional-looking schematics. Initializes predefined
        color schemes for different cell components.
        
        The generator automatically adapts to the current UI theme (light/dark)
        and provides appropriate colors and styling for all schematic elements.
        """
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
        """
        Generate comprehensive schematics for cylindrical battery cells.
        
        Creates both cross-section and side view schematics with proper scaling,
        dimensional annotations, and professional styling. The cross-section view
        shows the inner/outer diameter relationship with a 20:1 ratio, while the
        side view displays height and diameter dimensions with terminal placement.
        
        Args:
            diameter (float): Cell outer diameter in millimeters
            height (float): Cell height in millimeters
            
        Returns:
            Tuple[go.Figure, go.Figure]: A tuple containing:
                - Cross-section view figure (top-down circular view)
                - Side view figure (cylindrical profile with dimensions)
                
        The generated schematics include:
        - Proper dimensional scaling for optimal visualization
        - Interactive annotations showing key measurements
        - Theme-consistent colors and styling
        - Professional layout suitable for documentation
        """
        
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
        """
        Create detailed cross-section (top-down) view of a cylindrical cell.
        
        Generates a circular schematic showing the outer cell boundary and inner
        diameter relationship. Uses a 20:1 ratio between outer and inner diameters
        with clear annotations and professional styling.
        
        Args:
            diameter (float): Scaled diameter for optimal plot visualization
            
        Returns:
            go.Figure: Plotly figure showing circular cross-section with:
                - Outer cell boundary in blue
                - Inner diameter circle with dashed red outline
                - Dimensional annotations for both diameters
                - Center point marker for reference
                - Equal aspect ratio for accurate representation
        """
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
        
        # Add inner circle for inner diameter - very small with 20:1 ratio
        r_inner = r_outer * 0.05  # 20:1 ratio between outer and inner diameter
        x_inner = r_inner * np.cos(theta)
        y_inner = r_inner * np.sin(theta)
        
        fig.add_trace(go.Scatter(x=x_inner, y=y_inner, fill='toself',
                                fillcolor='rgba(255, 255, 255, 0.8)',  # White interior
                                line=dict(color='#e74c3c', width=4, dash='dash'),  # Thicker red dashed line
                                name='Inner Diameter'))
        
        # Add outer diameter annotation
        fig.add_annotation(x=0, y=r_outer + 0.15, text="D (Outer)", showarrow=True, 
                          arrowhead=2, arrowcolor="red", ax=0, ay=-20,
                          font=dict(size=12, color="red"))
        
        # Add inner diameter annotation inside the circle
        fig.add_annotation(x=0, y=0, text="d (Inner)", showarrow=False,
                          font=dict(size=16, color="red", family="Arial Black"))
        
        # Add center point
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', 
                                marker=dict(size=4, color='black'),
                                name='Center'))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Cross Section View",
            'xaxis': dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False, showticklabels=False,
                         range=[-r_outer-0.3, r_outer+0.3]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-r_outer-0.3, r_outer+0.3]),
            'showlegend': False,
            'height': 500,
            'margin': dict(l=10, r=10, t=30, b=10)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def _create_cylindrical_side_view(self, diameter: float, height: float) -> go.Figure:
        """
        Create detailed side view of a cylindrical cell with terminals.
        
        Generates a rectangular profile view showing the cell height and diameter
        with a top-mounted terminal. Includes dimensional annotations and professional
        styling consistent with technical documentation standards.
        
        Args:
            diameter (float): Scaled cell diameter for visualization
            height (float): Scaled cell height for visualization
            
        Returns:
            go.Figure: Plotly figure showing cylindrical side profile with:
                - Main cell body in blue with proper proportions
                - Top terminal in orange with realistic dimensions
                - Height (H) and diameter (D) annotations with arrows
                - Professional layout optimized for technical documentation
        """
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
            'title': "Side View",
            'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-d_half-0.2, d_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-0.2, height+terminal_height+0.2]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=10, r=10, t=30, b=10)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def create_pouch_schematics(self, height: float, width: float, length: float) -> Tuple[go.Figure, go.Figure]:
        """
        Generate comprehensive schematics for pouch battery cells.
        
        Creates both front and side view schematics showing the flexible pouch design
        with top-mounted terminals. Includes proper scaling, dimensional annotations,
        and professional styling suitable for technical documentation.
        
        Args:
            height (float): Cell height in millimeters
            width (float): Cell width in millimeters  
            length (float): Cell length/depth in millimeters
            
        Returns:
            Tuple[go.Figure, go.Figure]: A tuple containing:
                - Front view figure showing width x height dimensions
                - Side view figure showing length x height profile
                
        The generated schematics include:
        - Realistic pouch cell proportions and flexible edges
        - Top-mounted terminal configurations
        - Clear dimensional annotations
        - Professional layout for manufacturing specifications
        """
        
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
        """
        Create detailed front view of a pouch cell with top terminals.
        
        Generates a rectangular schematic showing the pouch cell's front face
        with closely-spaced top terminals and dimensional annotations. Uses
        realistic proportions and professional styling.
        
        Args:
            height (float): Scaled cell height for visualization
            width (float): Scaled cell width for visualization
            length (float): Scaled cell length (not used in front view but kept for consistency)
            
        Returns:
            go.Figure: Plotly figure showing pouch front view with:
                - Main pouch body in red with flexible edge representation
                - Positive and negative terminals in orange at the top
                - Height (H) and length (L) dimensional annotations
                - Equal aspect ratio for accurate proportional display
        """
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
        
        fig.add_annotation(x=w_half + 0.1, y=0, text="L", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Front View",
            'xaxis': dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False, showticklabels=False,
                         range=[-w_half-0.2, w_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=10, r=10, t=30, b=10)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def _create_pouch_side_view(self, height: float, width: float, length: float) -> go.Figure:
        """
        Create detailed side view of a pouch cell showing thickness profile.
        
        Generates a rectangular schematic showing the pouch cell's side profile
        with terminal configuration and dimensional annotations. Demonstrates
        the cell's width/thickness dimension clearly.
        
        Args:
            height (float): Scaled cell height for visualization
            width (float): Scaled cell width (not used in side view but kept for consistency)
            length (float): Scaled cell length/depth for side view width
            
        Returns:
            go.Figure: Plotly figure showing pouch side view with:
                - Main pouch body in red showing thickness profile
                - Terminal configuration in orange at the top
                - Height (H) and width (W) dimensional annotations
                - Professional layout for technical documentation
        """
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
        
        fig.add_annotation(x=l_half + 0.1, y=0, text="W", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Side View",
            'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-l_half-0.2, l_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=10, r=10, t=30, b=10)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def create_prismatic_schematics(self, height: float, width: float, length: float) -> Tuple[go.Figure, go.Figure]:
        """
        Generate comprehensive schematics for prismatic battery cells.
        
        Creates both front and side view schematics showing the rigid prismatic design
        with widely-spaced top terminals. Includes proper scaling, dimensional annotations,
        and professional styling suitable for technical documentation.
        
        Args:
            height (float): Cell height in millimeters
            width (float): Cell width in millimeters  
            length (float): Cell length/depth in millimeters
            
        Returns:
            Tuple[go.Figure, go.Figure]: A tuple containing:
                - Front view figure showing width x height dimensions
                - Side view figure showing length x height profile
                
        The generated schematics include:
        - Rigid rectangular cell housing in green
        - Widely-spaced terminal configurations for better current distribution
        - Clear dimensional annotations for manufacturing specifications
        - Professional layout optimized for hard case cell documentation
        """
        
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
        """
        Create detailed front view of a prismatic cell with widely-spaced terminals.
        
        Generates a rectangular schematic showing the prismatic cell's front face
        with widely-spaced top terminals for optimal current distribution. Uses
        green coloring to distinguish from pouch cells and professional styling.
        
        Args:
            height (float): Scaled cell height for visualization
            width (float): Scaled cell width for visualization
            length (float): Scaled cell length (not used in front view but kept for consistency)
            
        Returns:
            go.Figure: Plotly figure showing prismatic front view with:
                - Main prismatic body in green with rigid edge representation
                - Widely-spaced positive and negative terminals in orange
                - Height (H) and length (L) dimensional annotations
                - Equal aspect ratio for accurate proportional display
        """
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
        
        fig.add_annotation(x=w_half + 0.1, y=0, text="L", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Front View",
            'xaxis': dict(scaleanchor="y", scaleratio=1, showgrid=False, zeroline=False, showticklabels=False,
                         range=[-w_half-0.2, w_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=10, r=10, t=30, b=10)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def _create_prismatic_side_view(self, height: float, width: float, length: float) -> go.Figure:
        """
        Create detailed side view of a prismatic cell showing depth profile.
        
        Generates a rectangular schematic showing the prismatic cell's side profile
        with terminal configuration and dimensional annotations. Demonstrates
        the cell's length/depth dimension with rigid housing characteristics.
        
        Args:
            height (float): Scaled cell height for visualization
            width (float): Scaled cell width (not used in side view but kept for consistency)
            length (float): Scaled cell length/depth for side view width
            
        Returns:
            go.Figure: Plotly figure showing prismatic side view with:
                - Main prismatic body in green showing rigid depth profile
                - Terminal configuration in orange at the top
                - Height (H) and width (W) dimensional annotations
                - Professional layout for hard case cell documentation
        """
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
        
        fig.add_annotation(x=l_half + 0.1, y=0, text="W", showarrow=True,
                          arrowhead=2, arrowcolor="red", ax=-20, ay=0,
                          font=dict(size=14, color="red"))
        
        # Merge layout parameters to avoid conflicts
        layout_updates = {
            'title': "Side View",
            'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-l_half-0.2, l_half+0.2]),
            'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False,
                         range=[-h_half-0.2, h_half+0.4]),
            'showlegend': False,
            'height': 400,
            'margin': dict(l=10, r=10, t=30, b=10)
        }
        
        # Merge with theme layout
        theme_layout = self.plotly_theme['layout'].copy()
        theme_layout.update(layout_updates)
        fig.update_layout(**theme_layout)
        
        return fig
    
    def render_schematics(self, form_factor: str, dimensions: Dict[str, float]):
        """
        Render and display appropriate schematics based on cell form factor.
        
        Main rendering method that determines the cell type and displays the appropriate
        multi-view schematics in a Streamlit interface. Automatically scales charts
        for consistent presentation and creates a professional two-column layout.
        
        Args:
            form_factor (str): Cell form factor type ('cylindrical', 'pouch', 'prismatic')
            dimensions (Dict[str, float]): Dictionary containing cell dimensions:
                - For cylindrical: 'diameter' (mm), 'height' (mm)
                - For pouch: 'height' (mm), 'width' (mm), 'length' (mm) 
                - For prismatic: 'height' (mm), 'width' (mm), 'length' (mm)
                
        The method automatically:
        - Determines the appropriate schematic type based on form_factor
        - Creates multi-view schematics with professional styling
        - Displays them in a responsive two-column Streamlit layout
        - Applies consistent chart heights for uniform presentation
        - Uses fallback default dimensions if values are missing
        
        Supported Form Factors:
        - 'cylindrical': Shows cross-section and side views
        - 'pouch': Shows front and side views with flexible design
        - 'prismatic': Shows front and side views with rigid housing
        """
        
        # Set consistent height for all charts - reduced for compact layout
        chart_height = 200
        
        if form_factor == "cylindrical":
            diameter = dimensions.get('diameter', 18.0)
            height = dimensions.get('height', 65.0)
            
            st.markdown("### Cylindrical Cell Schematics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cross_section, side_view = self.create_cylindrical_schematics(diameter, height)
                # Set consistent height for both views to match other form factors
                cross_section.update_layout(height=chart_height)
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
