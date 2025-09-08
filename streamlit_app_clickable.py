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
import numpy as np
from scipy import stats

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
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
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
    
    .clickable-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-decoration: none;
    }
    
    .clickable-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-color: #1e3c72;
    }
    
    .clickable-card:active {
        transform: translateY(0px);
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
        # Make material selector card clickable
        material_selector_clicked = st.button("🔬 Material Selector", key="material_selector_card", use_container_width=True)
        if material_selector_clicked:
            st.session_state.current_page = 'material_selector'
            st.rerun()
        
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
    if st.button("← Back to Home", key="back_to_home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
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

def get_default_coa_data(material_name):
    """Get default CoA data based on material type"""
    default_data = {
        'NMC811': {
            'D_min': 0.5, 'D10': 2.1, 'D50': 8.5, 'D90': 18.2, 'D_max': 45.0,
            'BET': 0.8, 'tap_density': 2.4, 'bulk_density': 1.8, 'true_density': 4.7,
            'capacity': 200, 'voltage': 3.8, 'energy_density': 760, 'cycle_life': 1000,
            'moisture': 0.02, 'impurities': 50, 'pH': 11.5, 'crystallinity': 98.5
        },
        'LCO': {
            'D_min': 0.3, 'D10': 1.8, 'D50': 6.2, 'D90': 15.5, 'D_max': 35.0,
            'BET': 0.6, 'tap_density': 2.8, 'bulk_density': 2.1, 'true_density': 5.1,
            'capacity': 140, 'voltage': 3.9, 'energy_density': 546, 'cycle_life': 500,
            'moisture': 0.015, 'impurities': 30, 'pH': 10.8, 'crystallinity': 99.2
        },
        'NCA': {
            'D_min': 0.4, 'D10': 2.0, 'D50': 7.8, 'D90': 16.8, 'D_max': 40.0,
            'BET': 0.7, 'tap_density': 2.3, 'bulk_density': 1.7, 'true_density': 4.6,
            'capacity': 190, 'voltage': 3.7, 'energy_density': 703, 'cycle_life': 800,
            'moisture': 0.018, 'impurities': 40, 'pH': 11.2, 'crystallinity': 98.8
        }
    }
    return default_data.get(material_name, default_data['NMC811'])

def create_coa_display_table(coa_data):
    """Create a formatted table for CoA data display"""
    display_data = {
        'Category': [
            'Particle Size', 'Particle Size', 'Particle Size', 'Particle Size', 'Particle Size',
            'Surface & Density', 'Surface & Density', 'Surface & Density', 'Surface & Density',
            'Electrochemical', 'Electrochemical', 'Electrochemical', 'Electrochemical',
            'Chemical Composition', 'Chemical Composition', 'Chemical Composition', 'Chemical Composition'
        ],
        'Property': [
            'D-min', 'D10', 'D50', 'D90', 'D-max',
            'BET Surface Area', 'Tap Density', 'Bulk Density', 'True Density',
            'Specific Capacity', 'Nominal Voltage', 'Energy Density', 'Cycle Life',
            'Moisture Content', 'Total Impurities', 'pH Value', 'Crystallinity'
        ],
        'Value': [
            f"{coa_data['D_min']:.2f}", f"{coa_data['D10']:.2f}", f"{coa_data['D50']:.2f}", 
            f"{coa_data['D90']:.2f}", f"{coa_data['D_max']:.2f}",
            f"{coa_data['BET']:.2f}", f"{coa_data['tap_density']:.2f}", f"{coa_data['bulk_density']:.2f}", f"{coa_data['true_density']:.2f}",
            f"{coa_data['capacity']}", f"{coa_data['voltage']:.2f}", f"{coa_data['energy_density']}", f"{coa_data['cycle_life']}",
            f"{coa_data['moisture']:.3f}", f"{coa_data['impurities']}", f"{coa_data['pH']:.2f}", f"{coa_data['crystallinity']:.1f}"
        ],
        'Unit': [
            'μm', 'μm', 'μm', 'μm', 'μm',
            'm²/g', 'g/cm³', 'g/cm³', 'g/cm³',
            'mAh/g', 'V', 'Wh/kg', 'cycles',
            '%', 'ppm', '-', '%'
        ]
    }
    return pd.DataFrame(display_data)

def generate_psd_distribution(coa_data):
    """Generate particle size distribution data from D-values"""
    # Extract particle size data
    d_min = coa_data['D_min']
    d10 = coa_data['D10']
    d50 = coa_data['D50']
    d90 = coa_data['D90']
    d_max = coa_data['D_max']
    
    # Create a range of particle sizes
    particle_sizes = np.logspace(np.log10(d_min), np.log10(d_max), 100)
    
    # Estimate log-normal distribution parameters from D10, D50, D90
    # Using the relationship between percentiles and log-normal parameters
    ln_d50 = np.log(d50)
    ln_d10 = np.log(d10)
    ln_d90 = np.log(d90)
    
    # Estimate sigma (standard deviation of log-normal distribution)
    # Using the fact that for log-normal: ln(D84) - ln(D16) ≈ 2*sigma
    # We approximate using D90 and D10
    sigma = (ln_d90 - ln_d10) / (2 * stats.norm.ppf(0.9) - 2 * stats.norm.ppf(0.1))
    mu = ln_d50
    
    # Generate probability density function
    pdf = stats.lognorm.pdf(particle_sizes, s=sigma, scale=np.exp(mu))
    
    # Generate cumulative distribution function
    cdf = stats.lognorm.cdf(particle_sizes, s=sigma, scale=np.exp(mu)) * 100  # Convert to percentage
    
    # Calculate mean particle size
    mean_size = np.exp(mu + sigma**2 / 2)  # Mean of log-normal distribution
    
    return particle_sizes, pdf, cdf, mean_size

def generate_psd_plot(coa_data, plot_type, material_name):
    """Generate PSD plot based on CoA data"""
    try:
        # Generate distribution data
        particle_sizes, pdf, cdf, mean_size = generate_psd_distribution(coa_data)
        
        if plot_type == 'Both':
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=1, cols=1,
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f'{material_name} - Particle Size Distribution']
            )
            
            # Add normal distribution (PDF)
            fig.add_trace(
                go.Scatter(
                    x=particle_sizes,
                    y=pdf,
                    mode='lines',
                    name='Normal Distribution',
                    line=dict(color='blue', width=2),
                    yaxis='y'
                )
            )
            
            # Add cumulative distribution (CDF)
            fig.add_trace(
                go.Scatter(
                    x=particle_sizes,
                    y=cdf,
                    mode='lines',
                    name='Cumulative Distribution',
                    line=dict(color='red', width=2),
                    yaxis='y2'
                )
            )
            
            # Add mean radius line
            max_pdf = np.max(pdf)
            fig.add_trace(
                go.Scatter(
                    x=[mean_size, mean_size],
                    y=[0, max_pdf],
                    mode='lines',
                    name=f'Mean Radius ({mean_size:.2f} μm)',
                    line=dict(color='green', width=3, dash='dash'),
                    yaxis='y'
                )
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title='Particle Size (μm)',
                xaxis_type='log',
                height=500,
                showlegend=True,
                hovermode='x unified'
            )
            
            # Update y-axis labels
            fig.update_yaxes(title_text="Probability Density", secondary_y=False)
            fig.update_yaxes(title_text="Cumulative Percentage (%)", secondary_y=True)
            
        elif plot_type == 'Normal Distribution':
            fig = go.Figure()
            
            # Add normal distribution
            fig.add_trace(
                go.Scatter(
                    x=particle_sizes,
                    y=pdf,
                    mode='lines',
                    name='Normal Distribution',
                    line=dict(color='blue', width=2),
                    fill='tonexty'
                )
            )
            
            # Add mean radius line
            max_pdf = np.max(pdf)
            fig.add_trace(
                go.Scatter(
                    x=[mean_size, mean_size],
                    y=[0, max_pdf],
                    mode='lines',
                    name=f'Mean Radius ({mean_size:.2f} μm)',
                    line=dict(color='green', width=3, dash='dash')
                )
            )
            
            fig.update_layout(
                title=f'{material_name} - Normal Particle Size Distribution',
                xaxis_title='Particle Size (μm)',
                yaxis_title='Probability Density',
                xaxis_type='log',
                height=400,
                showlegend=True
            )
            
        else:  # Cumulative Distribution
            fig = go.Figure()
            
            # Add cumulative distribution
            fig.add_trace(
                go.Scatter(
                    x=particle_sizes,
                    y=cdf,
                    mode='lines',
                    name='Cumulative Distribution',
                    line=dict(color='red', width=2)
                )
            )
            
            # Add mean radius line
            # Calculate the CDF value at mean size
            sigma = (np.log(coa_data['D90']) - np.log(coa_data['D10'])) / (2 * stats.norm.ppf(0.9) - 2 * stats.norm.ppf(0.1))
            mu = np.log(coa_data['D50'])
            mean_cdf_value = stats.lognorm.cdf(mean_size, s=sigma, scale=coa_data['D50']) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=[mean_size, mean_size],
                    y=[0, mean_cdf_value],
                    mode='lines',
                    name=f'Mean Radius ({mean_size:.2f} μm)',
                    line=dict(color='green', width=3, dash='dash')
                )
            )
            
            # Add D10, D50, D90 markers
            fig.add_trace(
                go.Scatter(
                    x=[coa_data['D10'], coa_data['D50'], coa_data['D90']],
                    y=[10, 50, 90],
                    mode='markers',
                    name='D10, D50, D90',
                    marker=dict(color='orange', size=8, symbol='diamond')
                )
            )
            
            fig.update_layout(
                title=f'{material_name} - Cumulative Particle Size Distribution',
                xaxis_title='Particle Size (μm)',
                yaxis_title='Cumulative Percentage (%)',
                xaxis_type='log',
                height=400,
                showlegend=True
            )
        
        # Add annotations for key values (only for single plot types)
        if plot_type != 'Both':
            annotations = [
                dict(x=coa_data['D10'], y=10 if plot_type != 'Normal Distribution' else np.interp(coa_data['D10'], particle_sizes, pdf),
                     text=f"D10: {coa_data['D10']:.1f}μm", showarrow=True, arrowhead=2),
                dict(x=coa_data['D50'], y=50 if plot_type != 'Normal Distribution' else np.interp(coa_data['D50'], particle_sizes, pdf),
                     text=f"D50: {coa_data['D50']:.1f}μm", showarrow=True, arrowhead=2),
                dict(x=coa_data['D90'], y=90 if plot_type != 'Normal Distribution' else np.interp(coa_data['D90'], particle_sizes, pdf),
                     text=f"D90: {coa_data['D90']:.1f}μm", showarrow=True, arrowhead=2)
            ]
            fig.update_layout(annotations=annotations)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError as e:
        st.error("scipy library is required for PSD plotting. Please install it using: pip install scipy")
    except Exception as e:
        st.error(f"Error generating PSD plot: {str(e)}")
        st.info("Please check that all required libraries are installed and CoA data is valid.")

def render_cathode_materials_page():
    """Render the cathode materials page with dropdown, table, and plots"""
    if st.button("← Back to Material Selector", key="back_to_materials"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
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
            # CoA Upload Section
            st.markdown("#### Upload CoA File")
            uploaded_file = st.file_uploader(
                "Upload Certificate of Analysis (PDF)",
                type=['pdf'],
                key=f"coa_upload_{selected_cathode}",
                help="Upload a PDF file containing the Certificate of Analysis"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                if st.button("📄 Extract Data from PDF", key="extract_pdf"):
                    st.info("PDF data extraction feature coming soon!")
            
            st.markdown("#### CoA Sheet - Material Characterization")
            
            # Initialize CoA data in session state if not exists
            coa_key = f"coa_data_{selected_cathode}"
            if coa_key not in st.session_state:
                st.session_state[coa_key] = get_default_coa_data(selected_cathode)
            
            # Create editable form for CoA data
            with st.form(key=f"coa_form_{selected_cathode}"):
                st.markdown("**Particle Size Distribution (PSD)**")
                col_psd1, col_psd2 = st.columns(2)
                
                with col_psd1:
                    d_min = st.number_input("D-min (μm)", value=st.session_state[coa_key].get('D_min', 0.5), step=0.1, format="%.2f")
                    d10 = st.number_input("D10 (μm)", value=st.session_state[coa_key].get('D10', 2.1), step=0.1, format="%.2f")
                    d50 = st.number_input("D50 (μm)", value=st.session_state[coa_key].get('D50', 8.5), step=0.1, format="%.2f")
                
                with col_psd2:
                    d90 = st.number_input("D90 (μm)", value=st.session_state[coa_key].get('D90', 18.2), step=0.1, format="%.2f")
                    d_max = st.number_input("D-max (μm)", value=st.session_state[coa_key].get('D_max', 45.0), step=0.1, format="%.2f")
                
                st.markdown("**Surface Area & Density**")
                col_surf1, col_surf2 = st.columns(2)
                
                with col_surf1:
                    bet_surface = st.number_input("BET Surface Area (m²/g)", value=st.session_state[coa_key].get('BET', 0.8), step=0.1, format="%.2f")
                    tap_density = st.number_input("Tap Density (g/cm³)", value=st.session_state[coa_key].get('tap_density', 2.4), step=0.1, format="%.2f")
                
                with col_surf2:
                    bulk_density = st.number_input("Bulk Density (g/cm³)", value=st.session_state[coa_key].get('bulk_density', 1.8), step=0.1, format="%.2f")
                    true_density = st.number_input("True Density (g/cm³)", value=st.session_state[coa_key].get('true_density', 4.7), step=0.1, format="%.2f")
                
                st.markdown("**Electrochemical Properties**")
                col_electro1, col_electro2 = st.columns(2)
                
                with col_electro1:
                    capacity = st.number_input("Specific Capacity (mAh/g)", value=st.session_state[coa_key].get('capacity', 200), step=1, format="%d")
                    voltage = st.number_input("Nominal Voltage (V)", value=st.session_state[coa_key].get('voltage', 3.8), step=0.1, format="%.2f")
                
                with col_electro2:
                    energy_density = st.number_input("Energy Density (Wh/kg)", value=st.session_state[coa_key].get('energy_density', 760), step=1, format="%d")
                    cycle_life = st.number_input("Cycle Life (cycles)", value=st.session_state[coa_key].get('cycle_life', 1000), step=50, format="%d")
                
                st.markdown("**Chemical Composition**")
                col_chem1, col_chem2 = st.columns(2)
                
                with col_chem1:
                    moisture = st.number_input("Moisture Content (%)", value=st.session_state[coa_key].get('moisture', 0.02), step=0.01, format="%.3f")
                    impurities = st.number_input("Total Impurities (ppm)", value=st.session_state[coa_key].get('impurities', 50), step=10, format="%d")
                
                with col_chem2:
                    ph_value = st.number_input("pH Value", value=st.session_state[coa_key].get('pH', 11.5), step=0.1, format="%.2f")
                    crystallinity = st.number_input("Crystallinity (%)", value=st.session_state[coa_key].get('crystallinity', 98.5), step=0.1, format="%.2f")
                
                # Update button
                if st.form_submit_button("📊 Update CoA Data", use_container_width=True):
                    # Update session state with new values
                    st.session_state[coa_key] = {
                        'D_min': d_min, 'D10': d10, 'D50': d50, 'D90': d90, 'D_max': d_max,
                        'BET': bet_surface, 'tap_density': tap_density, 'bulk_density': bulk_density, 'true_density': true_density,
                        'capacity': capacity, 'voltage': voltage, 'energy_density': energy_density, 'cycle_life': cycle_life,
                        'moisture': moisture, 'impurities': impurities, 'pH': ph_value, 'crystallinity': crystallinity
                    }
                    st.success("✅ CoA data updated successfully!")
                    st.rerun()
            
            # Display current CoA data in a formatted table (read-only summary)
            st.markdown("#### Current CoA Summary")
            summary_df = create_coa_display_table(st.session_state[coa_key])
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # PSD Plot Section
            st.markdown("#### Particle Size Distribution")
            psd_plot_type = st.selectbox(
                "Select PSD Plot Type:",
                options=['Normal Distribution', 'Cumulative Distribution', 'Both'],
                key=f"psd_plot_type_{selected_cathode}"
            )
            
            if st.button("📊 Generate PSD Plot", key=f"generate_psd_{selected_cathode}"):
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
            # Use updated CoA data if available, otherwise use default material data
            coa_key = f"coa_data_{selected_cathode}"
            if coa_key in st.session_state:
                generate_excel_file(selected_cathode, material_data, st.session_state[coa_key])
            else:
                generate_excel_file(selected_cathode, material_data, None)

def generate_excel_file(material_name, material_data, coa_data=None):
    """Generate Excel file with model parameters"""
    # Create Excel file in memory
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # CoA Data sheet (if available)
        if coa_data:
            coa_df = create_coa_display_table(coa_data)
            coa_df.to_excel(writer, sheet_name='CoA_Data', index=False)
        
        # OCV sheet
        ocv_df = pd.DataFrame({
            'Voltage (V)': material_data['performance_data']['OCV']['voltage'],
            'Capacity (mAh/g)': material_data['performance_data']['OCV']['capacity']
        })
        ocv_df.to_excel(writer, sheet_name='OCV', index=False)
        
        # TOCV sheet (Temperature-dependent OCV)
        tocv_df = pd.DataFrame({
            'Temperature (°C)': [25, 45, 60],
            'OCV_25C (V)': material_data['performance_data']['OCV']['voltage'],
            'OCV_45C (V)': [v + 0.05 for v in material_data['performance_data']['OCV']['voltage']],
            'OCV_60C (V)': [v + 0.1 for v in material_data['performance_data']['OCV']['voltage']]
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
        
        # Material Properties sheet (using CoA data if available)
        if coa_data:
            properties_df = pd.DataFrame({
                'Property': ['Particle D50', 'BET Surface Area', 'Tap Density', 'True Density', 
                           'Specific Capacity', 'Nominal Voltage', 'Energy Density'],
                'Value': [coa_data['D50'], coa_data['BET'], coa_data['tap_density'], 
                         coa_data['true_density'], coa_data['capacity'], coa_data['voltage'], coa_data['energy_density']],
                'Unit': ['μm', 'm²/g', 'g/cm³', 'g/cm³', 'mAh/g', 'V', 'Wh/kg']
            })
            properties_df.to_excel(writer, sheet_name='Material_Properties', index=False)
    
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