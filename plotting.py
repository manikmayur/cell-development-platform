"""
Plotting functions for the Cell Development Platform
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils import generate_psd_distribution, load_performance_data_from_json


def generate_psd_plot(coa_data, plot_type, material_name):
    """Generate PSD plot based on CoA data"""
    try:
        # Generate PSD distribution data
        particle_sizes, pdf, cdf, mean_size = generate_psd_distribution(coa_data)
        
        if plot_type == 'Normal Distribution':
            # Create normal distribution plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=particle_sizes,
                y=pdf,
                mode='lines',
                name='PSD',
                line=dict(color='blue', width=2)
            ))
            
            # Add D-values as vertical lines
            d_values = [coa_data['D10'], coa_data['D50'], coa_data['D90']]
            d_labels = ['D10', 'D50', 'D90']
            colors = ['red', 'green', 'orange']
            
            for d_val, label, color in zip(d_values, d_labels, colors):
                fig.add_vline(x=d_val, line_dash="dash", line_color=color, 
                            annotation_text=label, annotation_position="top")
            
            fig.update_layout(
                title=f'{material_name} - Particle Size Distribution',
                xaxis_title='Particle Size (μm)',
                yaxis_title='Probability Density',
                height=400
            )
            
        elif plot_type == 'Cumulative Distribution':
            # Create cumulative distribution plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=particle_sizes,
                y=cdf * 100,  # Convert to percentage
                mode='lines',
                name='Cumulative PSD',
                line=dict(color='purple', width=2)
            ))
            
            # Add D-values as horizontal and vertical lines
            d_values = [coa_data['D10'], coa_data['D50'], coa_data['D90']]
            d_labels = ['D10', 'D50', 'D90']
            colors = ['red', 'green', 'orange']
            
            for d_val, label, color in zip(d_values, d_labels, colors):
                fig.add_vline(x=d_val, line_dash="dash", line_color=color, 
                            annotation_text=label, annotation_position="top")
                fig.add_hline(y=10 if label == 'D10' else (50 if label == 'D50' else 90), 
                            line_dash="dash", line_color=color, opacity=0.5)
            
            fig.update_layout(
                title=f'{material_name} - Cumulative Particle Size Distribution',
                xaxis_title='Particle Size (μm)',
                yaxis_title='Cumulative Percentage (%)',
                height=400
            )
            
        else:  # Both
            # Create subplot with both distributions
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Normal Distribution', 'Cumulative Distribution'),
                vertical_spacing=0.1
            )
            
            # Normal distribution
            fig.add_trace(go.Scatter(
                x=particle_sizes,
                y=pdf,
                mode='lines',
                name='PSD',
                line=dict(color='blue', width=2)
            ), row=1, col=1)
            
            # Cumulative distribution
            fig.add_trace(go.Scatter(
                x=particle_sizes,
                y=cdf * 100,
                mode='lines',
                name='Cumulative PSD',
                line=dict(color='purple', width=2)
            ), row=2, col=1)
            
            # Add D-values to both subplots
            d_values = [coa_data['D10'], coa_data['D50'], coa_data['D90']]
            d_labels = ['D10', 'D50', 'D90']
            colors = ['red', 'green', 'orange']
            
            for d_val, label, color in zip(d_values, d_labels, colors):
                # Add to normal distribution
                fig.add_vline(x=d_val, line_dash="dash", line_color=color, 
                            annotation_text=label, annotation_position="top", row=1, col=1)
                # Add to cumulative distribution
                fig.add_vline(x=d_val, line_dash="dash", line_color=color, 
                            annotation_text=label, annotation_position="top", row=2, col=1)
                fig.add_hline(y=10 if label == 'D10' else (50 if label == 'D50' else 90), 
                            line_dash="dash", line_color=color, opacity=0.5, row=2, col=1)
            
            fig.update_layout(
                title=f'{material_name} - Particle Size Distribution Analysis',
                height=600,
                showlegend=False
            )
            
            fig.update_xaxes(title_text="Particle Size (μm)", row=2, col=1)
            fig.update_yaxes(title_text="Probability Density", row=1, col=1)
            fig.update_yaxes(title_text="Cumulative Percentage (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Size", f"{mean_size:.2f} μm")
        with col2:
            st.metric("D10", f"{coa_data['D10']:.2f} μm")
        with col3:
            st.metric("D50", f"{coa_data['D50']:.2f} μm")
        with col4:
            st.metric("D90", f"{coa_data['D90']:.2f} μm")
            
    except ImportError as e:
        st.error("scipy library is required for PSD plotting. Please install it using: pip install scipy")
    except Exception as e:
        st.error(f"Error generating PSD plot: {str(e)}")
        st.info("Please check that all required libraries are installed and CoA data is valid.")


def create_performance_plot(material_name, plot_type, material_data):
    """Create performance plots (OCV, GITT, EIS)"""
    # Load performance data from individual JSON files
    performance_data = load_performance_data_from_json(material_name, plot_type)
    
    # Create performance plot
    if plot_type == 'OCV':
        fig = px.line(
            x=performance_data['capacity'],
            y=performance_data['voltage'],
            title=f'{material_data["name"]} - Open Circuit Voltage',
            labels={'x': 'Capacity (mAh/g)', 'y': 'Voltage (V)'}
        )
    elif plot_type == 'GITT':
        fig = px.line(
            x=performance_data['time'],
            y=performance_data['voltage'],
            title=f'{material_data["name"]} - GITT Analysis',
            labels={'x': 'Time (h)', 'y': 'Voltage (V)'}
        )
    else:  # EIS
        fig = px.line(
            x=performance_data['frequency'],
            y=performance_data['impedance'],
            title=f'{material_data["name"]} - Electrochemical Impedance Spectroscopy',
            labels={'x': 'Frequency (Hz)', 'y': 'Impedance (Ω)'}
        )
    
    fig.update_layout(height=400)
    return fig


def create_cycle_life_plots(material_data):
    """Create cycle life and coulombic efficiency plots"""
    # Cycle life plot
    cycle_fig = px.line(
        x=material_data['cycle_life']['cycles'],
        y=material_data['cycle_life']['capacity_retention'],
        title='Cycle Life Performance',
        labels={'x': 'Cycles', 'y': 'Capacity Retention (%)'}
    )
    cycle_fig.update_layout(height=300)
    
    # Coulombic efficiency plot
    eff_fig = px.line(
        x=material_data['coulombic_efficiency']['cycles'],
        y=material_data['coulombic_efficiency']['efficiency'],
        title='Coulombic Efficiency',
        labels={'x': 'Cycles', 'y': 'Efficiency (%)'}
    )
    eff_fig.update_layout(height=300)
    
    return cycle_fig, eff_fig
