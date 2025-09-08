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
    """Create a formatted table for CoA data display with merged category rows"""
    # Group properties by category
    categories = {
        'Particle Size': [
            ('D-min', coa_data['D_min'], 'μm'),
            ('D10', coa_data['D10'], 'μm'),
            ('D50', coa_data['D50'], 'μm'),
            ('D90', coa_data['D90'], 'μm'),
            ('D-max', coa_data['D_max'], 'μm')
        ],
        'Surface & Density': [
            ('BET Surface Area', coa_data['BET'], 'm²/g'),
            ('Tap Density', coa_data['tap_density'], 'g/cm³'),
            ('Bulk Density', coa_data['bulk_density'], 'g/cm³'),
            ('True Density', coa_data['true_density'], 'g/cm³')
        ],
        'Electrochemical': [
            ('Specific Capacity', coa_data['capacity'], 'mAh/g'),
            ('Nominal Voltage', coa_data['voltage'], 'V'),
            ('Energy Density', coa_data['energy_density'], 'Wh/kg'),
            ('Cycle Life', coa_data['cycle_life'], 'cycles')
        ],
        'Chemical Composition': [
            ('Moisture Content', coa_data['moisture'], '%'),
            ('Total Impurities', coa_data['impurities'], 'ppm'),
            ('pH Value', coa_data['pH'], '-'),
            ('Crystallinity', coa_data['crystallinity'], '%')
        ]
    }
    
    # Create display data with merged categories
    display_data = {'Category': [], 'Property': [], 'Value': [], 'Unit': []}
    
    for category, properties in categories.items():
        for i, (prop, value, unit) in enumerate(properties):
            if i == 0:
                # First row shows category name
                display_data['Category'].append(category)
            else:
                # Subsequent rows have empty category (will be merged in display)
                display_data['Category'].append('')
            
            display_data['Property'].append(prop)
            if unit in ['μm', 'm²/g', 'g/cm³', 'V', '%']:
                display_data['Value'].append(f"{value:.2f}")
            elif unit in ['mAh/g', 'Wh/kg', 'cycles', 'ppm']:
                display_data['Value'].append(f"{value:.0f}")
            else:
                display_data['Value'].append(f"{value:.3f}")
            display_data['Unit'].append(unit)
    
    return pd.DataFrame(display_data)

def save_coa_to_json(coa_data, material_name):
    """Save CoA data to JSON file for plot functions to read"""
    import json
    import os
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save to JSON file
    filename = f"{data_dir}/{material_name.lower()}_coa.json"
    with open(filename, 'w') as f:
        json.dump(coa_data, f, indent=2)
    
    return filename

def save_performance_data_to_json(performance_data, material_name, data_type):
    """Save performance data (OCV, GITT, EIS) to individual JSON files"""
    import json
    import os
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save to JSON file
    filename = f"{data_dir}/{material_name.lower()}_{data_type.lower()}.json"
    with open(filename, 'w') as f:
        json.dump(performance_data, f, indent=2)
    
    return filename

def load_performance_data_from_json(material_name, data_type):
    """Load performance data (OCV, GITT, EIS) from individual JSON files"""
    import json
    import os
    
    filename = f"data/{material_name.lower()}_{data_type.lower()}.json"
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        # Return default data if file doesn't exist
        return get_default_performance_data(data_type)

def get_default_performance_data(data_type):
    """Get default performance data for a given type"""
    defaults = {
        'OCV': {'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2], 'capacity': [0, 50, 100, 150, 180, 195, 200]},
        'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]},
        'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [100, 50, 25, 15, 10, 8]}
    }
    return defaults.get(data_type, {})

def get_default_anode_data(material_name):
    """Get default anode material data"""
    default_data = {
        'Graphite': {
            'name': 'Graphite (C)',
            'coa_data': {
                'D_min': 5.0, 'D10': 8.2, 'D50': 15.5, 'D90': 28.0, 'D_max': 50.0,
                'BET': 2.5, 'tap_density': 1.0, 'bulk_density': 0.8, 'true_density': 2.2,
                'capacity': 372, 'voltage': 0.1, 'energy_density': 37, 'cycle_life': 2000,
                'moisture': 0.01, 'impurities': 20, 'pH': 7.0, 'crystallinity': 95.0
            },
            'performance_data': {
                'OCV': {'voltage': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35], 'capacity': [0, 60, 120, 180, 240, 300, 372]},
                'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]},
                'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [50, 25, 12, 8, 5, 3]}
            }
        },
        'Silicon': {
            'name': 'Silicon (Si)',
            'coa_data': {
                'D_min': 1.0, 'D10': 2.5, 'D50': 5.0, 'D90': 10.0, 'D_max': 20.0,
                'BET': 15.0, 'tap_density': 0.8, 'bulk_density': 0.6, 'true_density': 2.3,
                'capacity': 4200, 'voltage': 0.4, 'energy_density': 1680, 'cycle_life': 500,
                'moisture': 0.005, 'impurities': 100, 'pH': 7.5, 'crystallinity': 90.0
            },
            'performance_data': {
                'OCV': {'voltage': [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], 'capacity': [0, 800, 1600, 2400, 3200, 3800, 4200]},
                'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]},
                'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [200, 100, 50, 30, 20, 15]}
            }
        },
        'Tin': {
            'name': 'Tin (Sn)',
            'coa_data': {
                'D_min': 2.0, 'D10': 4.0, 'D50': 8.0, 'D90': 15.0, 'D_max': 25.0,
                'BET': 8.0, 'tap_density': 3.5, 'bulk_density': 2.8, 'true_density': 7.3,
                'capacity': 994, 'voltage': 0.6, 'energy_density': 596, 'cycle_life': 300,
                'moisture': 0.008, 'impurities': 80, 'pH': 6.8, 'crystallinity': 85.0
            },
            'performance_data': {
                'OCV': {'voltage': [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 'capacity': [0, 200, 400, 600, 800, 950, 994]},
                'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]},
                'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [150, 75, 35, 20, 12, 8]}
            }
        }
    }
    return default_data.get(material_name, default_data['Graphite'])

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
            
            # Create editable CoA data table
            st.markdown("**📊 Edit CoA Data**")
            
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
            
            # Create editable table
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
                
                st.success(f"✅ CoA data updated successfully! Saved to {json_filename}")
                st.rerun()
            
            
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
            
            # Load performance data from individual JSON files
            performance_data = load_performance_data_from_json(selected_cathode, plot_type)
            
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
        
        # Load performance data from JSON files
        ocv_data = load_performance_data_from_json(material_name, 'OCV')
        gitt_data = load_performance_data_from_json(material_name, 'GITT')
        eis_data = load_performance_data_from_json(material_name, 'EIS')
        
        # OCV sheet
        ocv_df = pd.DataFrame({
            'Voltage (V)': ocv_data['voltage'],
            'Capacity (mAh/g)': ocv_data['capacity']
        })
        ocv_df.to_excel(writer, sheet_name='OCV', index=False)
        
        # GITT sheet
        gitt_df = pd.DataFrame({
            'Time (h)': gitt_data['time'],
            'Voltage (V)': gitt_data['voltage']
        })
        gitt_df.to_excel(writer, sheet_name='GITT', index=False)
        
        # EIS sheet
        eis_df = pd.DataFrame({
            'Frequency (Hz)': eis_data['frequency'],
            'Impedance (Ω)': eis_data['impedance']
        })
        eis_df.to_excel(writer, sheet_name='EIS', index=False)
        
        # TOCV sheet (Temperature-dependent OCV)
        tocv_df = pd.DataFrame({
            'Temperature (°C)': [25, 45, 60],
            'OCV_25C (V)': ocv_data['voltage'],
            'OCV_45C (V)': [v + 0.05 for v in ocv_data['voltage']],
            'OCV_60C (V)': [v + 0.1 for v in ocv_data['voltage']]
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
        
        # Load performance data from individual JSON files
        performance_data = load_performance_data_from_json(f"anode_{selected_anode}", plot_type)
        
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

def render_anode_materials_page():
    """Render the anode materials page with dropdown, table, and plots"""
    if st.button("← Back to Material Selector", key="back_to_materials_anode"):
        st.session_state.current_page = 'material_selector'
        st.rerun()
    
    st.markdown("### 🔋 Anode Materials")
    st.markdown("Select and analyze anode materials for your battery cell.")
    
    # Anode material selection
    anode_materials = ["Graphite", "Silicon", "Tin"]
    selected_anode = st.selectbox(
        "Select Anode Material:",
        anode_materials,
        key="anode_material_selector"
    )
    
    if selected_anode:
        st.session_state.selected_anode = selected_anode
        
        # Get default anode data
        anode_data = get_default_anode_data(selected_anode)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📋 CoA Data", "📊 PSD Plot", "⚡ Performance", "📈 Export"])
        
        with tab1:
            st.markdown(f"#### {selected_anode} - Certificate of Analysis")
            
            # Create editable CoA data
            coa_data = anode_data['coa']
            editable_data = []
            
            for category, properties in coa_data.items():
                for prop, value in properties.items():
                    editable_data.append({
                        "Category": category,
                        "Property": prop,
                        "Value": value
                    })
            
            # Display editable table
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
            
            # Update CoA data
            if st.button("📊 Update CoA Data", key=f"update_anode_coa_{selected_anode}", use_container_width=True):
                # Extract updated values
                updated_coa_data = {}
                for _, row in edited_df.iterrows():
                    category = row['Category']
                    property_name = row['Property']
                    value = row['Value']
                    
                    if category not in updated_coa_data:
                        updated_coa_data[category] = {}
                    updated_coa_data[category][property_name] = value
                
                # Update session state
                if 'anode_coa_data' not in st.session_state:
                    st.session_state.anode_coa_data = {}
                st.session_state.anode_coa_data[selected_anode] = updated_coa_data
                
                # Save to JSON
                json_filename = save_coa_to_json(updated_coa_data, f"anode_{selected_anode}")
                
                # Update AI context
                if 'ai_context' in st.session_state:
                    update_ai_context(f"Updated CoA data for anode {selected_anode}")
                
                st.success(f"✅ CoA data updated successfully! Saved to {json_filename}")
                st.rerun()
        
        with tab2:
            st.markdown(f"#### {selected_anode} - Particle Size Distribution")
            
            # Generate PSD plot
            psd_data = anode_data['psd']
            fig = generate_psd_plot(psd_data, f"{selected_anode} Anode")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown(f"#### {selected_anode} - Performance Data")
            
            # Load performance data from JSON files
            ocv_data = load_performance_data_from_json(f"anode_{selected_anode}", "OCV")
            gitt_data = load_performance_data_from_json(f"anode_{selected_anode}", "GITT")
            eis_data = load_performance_data_from_json(f"anode_{selected_anode}", "EIS")
            
            # Create performance plots
            col1, col2 = st.columns(2)
            
            with col1:
                # OCV plot
                fig_ocv = create_performance_plot(ocv_data, f"{selected_anode} OCV", "Voltage (V)", "Capacity (mAh/g)")
                st.plotly_chart(fig_ocv, use_container_width=True)
                
                # GITT plot
                fig_gitt = create_performance_plot(gitt_data, f"{selected_anode} GITT", "Time (s)", "Voltage (V)")
                st.plotly_chart(fig_gitt, use_container_width=True)
            
            with col2:
                # EIS plot
                fig_eis = create_performance_plot(eis_data, f"{selected_anode} EIS", "Z' (Ω)", "Z'' (Ω)")
                st.plotly_chart(fig_eis, use_container_width=True)
                
                # Cycle life plot
                cycle_data = anode_data.get('cycle_life', {})
                if cycle_data:
                    fig_cycle = create_cycle_life_plots(cycle_data, f"{selected_anode} Cycle Life")
                    st.plotly_chart(fig_cycle, use_container_width=True)
        
        with tab4:
            st.markdown(f"#### Export {selected_anode} Data")
            
            if st.button("📥 Download Excel File", key=f"export_anode_{selected_anode}", use_container_width=True):
                try:
                    # Create Excel export
                    excel_data = create_excel_export(
                        material_name=selected_anode,
                        material_type="anode",
                        coa_data=anode_data['coa'],
                        psd_data=anode_data['psd'],
                        ocv_data=ocv_data,
                        gitt_data=gitt_data,
                        eis_data=eis_data,
                        cycle_data=anode_data.get('cycle_life', {})
                    )
                    
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
            soc = np.linspace(0, 100, 100)
            voltage = 3.7 - 0.5 * (soc/100) + 0.2 * np.sin(2 * np.pi * soc/100)
            
            fig = px.line(x=soc, y=voltage, title="Voltage vs State of Charge")
            fig.update_layout(xaxis_title="State of Charge (%)", yaxis_title="Voltage (V)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select a form factor first!")

def render_chat_interface():
    """Render the enhanced context-aware chat interface with fixed height and scrolling"""
    st.markdown("### 🤖 AI Assistant")
    
    # Initialize chat history and context
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'ai_context' not in st.session_state:
        st.session_state.ai_context = {
            'current_page': 'home',
            'selected_materials': {},
            'recent_actions': []
        }
    
    # Display current context
    with st.expander("📊 Current Context", expanded=False):
        context = st.session_state.ai_context
        st.write(f"**Current Page:** {context['current_page'].replace('_', ' ').title()}")
        if context['selected_materials']:
            # Filter out None values and join
            selected = [v for v in context['selected_materials'].values() if v is not None]
            if selected:
                st.write(f"**Selected Materials:** {', '.join(selected)}")
        if context['recent_actions']:
            # Filter out None values and join
            actions = [a for a in context['recent_actions'][-3:] if a is not None]
            if actions:
                st.write(f"**Recent Actions:** {', '.join(actions)}")
    
    # Create fixed height chat container with scrolling
    st.markdown("""
    <style>
    .chat-container {
        height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        background-color: #f8f9fa;
        margin-bottom: 10px;
    }
    .chat-message {
        margin-bottom: 10px;
        padding: 8px;
        border-radius: 8px;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20px;
    }
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: 20px;
    }
    </style>
    
    <script>
    function scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Scroll to bottom when page loads
    window.addEventListener('load', scrollToBottom);
    
    // Scroll to bottom when new messages are added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                scrollToBottom();
            }
        });
    });
    
    // Start observing
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        observer.observe(chatContainer, { childList: true, subtree: true });
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Chat history container
    chat_container = st.container()
    with chat_container:
        # Add scroll to bottom button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("⬇️", key="scroll_bottom", help="Scroll to bottom"):
                st.markdown("""
                <script>
                const chatContainer = document.querySelector('.chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                </script>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message"><strong>AI:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Context-aware suggestions
    suggestions = get_contextual_suggestions()
    if suggestions:
        st.markdown("**💡 Suggestions:**")
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggestion_{suggestion}", use_container_width=True):
                # Add suggestion as user message
                st.session_state.chat_history.append({"role": "user", "content": suggestion})
                response = process_enhanced_chat_command(suggestion)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about battery materials, cell design, or navigation..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Show typing indicator
        with st.spinner("🤖 AI is thinking..."):
            # Process the command with OpenAI integration
            response = process_enhanced_chat_command(prompt)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()

def get_contextual_suggestions():
    """Get context-aware suggestions based on current page and state"""
    current_page = st.session_state.get('current_page', 'home')
    suggestions = []
    
    if current_page == 'home':
        suggestions = [
            "Show me material selector",
            "Open cathode materials",
            "Design a new cell",
            "What materials are available?"
        ]
    elif current_page == 'material_selector':
        suggestions = [
            "Select NMC811 cathode",
            "Choose graphite anode",
            "Show me all materials",
            "Go to cell design"
        ]
    elif current_page == 'cathode_materials':
        selected = st.session_state.get('selected_cathode', '')
        suggestions = [
            f"Analyze {selected} properties",
            "Update CoA data",
            "Generate performance plots",
            "Export to Excel"
        ]
    elif current_page == 'cell_design':
        suggestions = [
            "Select cylindrical form factor",
            "Choose NMC811 cathode",
            "Run simulation",
            "Compare form factors"
        ]
    
    return suggestions

def update_ai_context(action: str, details: dict = None):
    """Update AI context with recent actions"""
    if 'ai_context' not in st.session_state:
        st.session_state.ai_context = {
            'current_page': 'home',
            'selected_materials': {},
            'recent_actions': []
        }
    
    # Update current page
    st.session_state.ai_context['current_page'] = st.session_state.get('current_page', 'home')
    
    # Update selected materials (only if not None)
    if 'selected_cathode' in st.session_state and st.session_state.selected_cathode is not None:
        st.session_state.ai_context['selected_materials']['cathode'] = st.session_state.selected_cathode
    if 'selected_anode' in st.session_state and st.session_state.selected_anode is not None:
        st.session_state.ai_context['selected_materials']['anode'] = st.session_state.selected_anode
    if 'selected_form_factor' in st.session_state and st.session_state.selected_form_factor is not None:
        st.session_state.ai_context['selected_materials']['form_factor'] = st.session_state.selected_form_factor
    
    # Add recent action (only if not None)
    if action is not None:
        st.session_state.ai_context['recent_actions'].append(action)
        if len(st.session_state.ai_context['recent_actions']) > 5:
            st.session_state.ai_context['recent_actions'] = st.session_state.ai_context['recent_actions'][-5:]

def get_comprehensive_context():
    """Get comprehensive context for OpenAI"""
    context = {
        "current_page": st.session_state.get('current_page', 'home'),
        "selected_materials": {},
        "recent_actions": st.session_state.get('ai_context', {}).get('recent_actions', []),
        "available_pages": [
            "home", "material_selector", "cathode_materials", "anode_materials", 
            "cell_design", "electrolyte_materials", "separator_materials"
        ],
        "available_cathodes": ["NMC811", "LCO", "NCA"],
        "available_anodes": ["Graphite", "Silicon", "Tin"],
        "available_form_factors": ["cylindrical", "pouch", "prismatic"],
        "available_electrolytes": ["LiPF6 in EC:DMC", "LiPF6 in EC:EMC", "LiTFSI in EC:DMC"],
        "available_separators": ["PE", "PP", "PE/PP Trilayer"]
    }
    
    # Add selected materials if they exist
    if 'selected_cathode' in st.session_state and st.session_state.selected_cathode:
        context["selected_materials"]["cathode"] = st.session_state.selected_cathode
    if 'selected_anode' in st.session_state and st.session_state.selected_anode:
        context["selected_materials"]["anode"] = st.session_state.selected_anode
    if 'selected_form_factor' in st.session_state and st.session_state.selected_form_factor:
        context["selected_materials"]["form_factor"] = st.session_state.selected_form_factor
    
    return context

def call_openai_with_context(prompt: str) -> str:
    """Call OpenAI with comprehensive context"""
    try:
        context = get_comprehensive_context()
        
        # Create system prompt with context
        system_prompt = f"""You are an AI assistant for a Battery Cell Development Platform. You have access to the current application state and can help users navigate, analyze materials, and design battery cells.

CURRENT APPLICATION CONTEXT:
- Current Page: {context['current_page']}
- Selected Materials: {context['selected_materials']}
- Recent Actions: {context['recent_actions'][-3:] if context['recent_actions'] else 'None'}

AVAILABLE OPTIONS:
- Pages: {', '.join(context['available_pages'])}
- Cathode Materials: {', '.join(context['available_cathodes'])}
- Anode Materials: {', '.join(context['available_anodes'])}
- Form Factors: {', '.join(context['available_form_factors'])}
- Electrolytes: {', '.join(context['available_electrolytes'])}
- Separators: {', '.join(context['available_separators'])}

CAPABILITIES:
- Navigate between pages
- Select and analyze battery materials
- Design battery cells with different form factors
- Provide material recommendations and analysis
- Explain battery chemistry and performance
- Help with data interpretation and visualization

NAVIGATION COMMANDS (use these to control the app):
- To navigate to a page, respond with: NAVIGATE_TO:page_name
- To select a material, respond with: SELECT_MATERIAL:material_type:material_name
- To select form factor, respond with: SELECT_FORM_FACTOR:form_factor_name

Be helpful, informative, and provide detailed explanations about battery materials, cell design, and performance characteristics. Use emojis to make responses engaging."""

        # Call OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback to local response if OpenAI fails
        return get_fallback_response(prompt)

def get_fallback_response(prompt: str) -> str:
    """Fallback response when OpenAI is not available"""
    prompt_lower = prompt.lower()
    context = get_comprehensive_context()
    current_page = context['current_page']
    
    # Basic navigation fallback
    if any(word in prompt_lower for word in ["home", "main", "start"]):
        return "🏠 I can help you navigate to the home page. Use the navigation buttons or ask me to 'go home'."
    
    elif any(word in prompt_lower for word in ["material", "selector", "materials"]):
        return "🔬 I can help you with material selection. Available cathode materials: NMC811, LCO, NCA. Available anode materials: Graphite, Silicon, Tin."
    
    elif any(word in prompt_lower for word in ["cathode", "nmc811", "lco", "nca"]):
        return "⚡ I can help you analyze cathode materials. NMC811 offers high energy density, LCO has high voltage, and NCA provides excellent power capability."
    
    elif any(word in prompt_lower for word in ["anode", "graphite", "silicon", "tin"]):
        return "🔋 I can help you with anode materials. Graphite is the most stable, Silicon offers high capacity, and Tin provides good performance."
    
    elif any(word in prompt_lower for word in ["design", "cell design", "form factor"]):
        return "🔧 I can help you design battery cells. Available form factors: cylindrical (high energy density), pouch (flexible shape), prismatic (good thermal management)."
    
    elif any(word in prompt_lower for word in ["help", "what can you do"]):
        return f"""🤖 **I'm your AI assistant for the Battery Cell Development Platform!**

**Current Context:** You're on the {current_page.replace('_', ' ').title()} page.

**I can help you with:**
- 🔬 Navigate between different pages
- ⚡ Select and analyze battery materials  
- 🔧 Design battery cells with different form factors
- 📊 Provide material recommendations and analysis
- 💡 Explain battery chemistry and performance

**Try asking:**
- "Show me NMC811 properties"
- "Design a cylindrical cell"
- "What's the best cathode for high energy?"
- "Navigate to material selector"

What would you like to explore?"""
    
    else:
        return f"""I understand you're asking about "{prompt}". 

**Current Context:** You're on the {current_page.replace('_', ' ').title()} page.

I can help you with:
- Material selection and analysis
- Cell design and form factors  
- Performance simulation
- Navigation between pages

Try asking something like "Show me NMC811 properties" or "Design a cylindrical cell"."""

def process_enhanced_chat_command(prompt: str) -> str:
    """Enhanced chat command processing with OpenAI integration"""
    # Update context
    update_ai_context(f"User asked: {prompt}")
    
    # Get OpenAI response
    response = call_openai_with_context(prompt)
    
    # Check for navigation commands in the response
    if "NAVIGATE_TO:" in response:
        # Extract page name and navigate
        page_name = response.split("NAVIGATE_TO:")[1].split()[0]
        if page_name in ["home", "material_selector", "cathode_materials", "anode_materials", "cell_design", "electrolyte_materials", "separator_materials"]:
            st.session_state.current_page = page_name
            st.rerun()
        # Remove the navigation command from response
        response = response.split("NAVIGATE_TO:")[0].strip()
    
    elif "SELECT_MATERIAL:" in response:
        # Extract material selection and update state
        parts = response.split("SELECT_MATERIAL:")[1].split(":")
        if len(parts) >= 2:
            material_type = parts[0]
            material_name = parts[1].split()[0]
            
            if material_type == "cathode" and material_name in ["NMC811", "LCO", "NCA"]:
                st.session_state.current_page = 'cathode_materials'
                st.session_state.selected_cathode = material_name
                st.rerun()
            elif material_type == "anode" and material_name in ["Graphite", "Silicon", "Tin"]:
                st.session_state.current_page = 'anode_materials'
                st.session_state.selected_anode = material_name
                st.rerun()
        # Remove the selection command from response
        response = response.split("SELECT_MATERIAL:")[0].strip()
    
    elif "SELECT_FORM_FACTOR:" in response:
        # Extract form factor selection and update state
        form_factor = response.split("SELECT_FORM_FACTOR:")[1].split()[0]
        if form_factor in ["cylindrical", "pouch", "prismatic"]:
            st.session_state.current_page = 'cell_design'
            st.session_state.selected_form_factor = form_factor
            st.rerun()
        # Remove the selection command from response
        response = response.split("SELECT_FORM_FACTOR:")[0].strip()
    
    return response

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
            render_anode_materials_page()
        elif st.session_state.current_page == 'cell_design':
            render_cell_design_page()
        elif st.session_state.current_page == 'electrolyte_materials':
            st.markdown("### Electrolyte Materials")
            st.info("Electrolyte materials page coming soon!")
        elif st.session_state.current_page == 'separator_materials':
            st.markdown("### Separator Materials")
            st.info("Separator materials page coming soon!")
        
        # Update AI context after page rendering
        if 'ai_context' in st.session_state:
            update_ai_context(f"Navigated to {st.session_state.current_page}")
    
    with col2:
        # Chat interface (20%)
        render_chat_interface()

if __name__ == "__main__":
    main()