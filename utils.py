"""
Utility functions for the Cell Development Platform
"""
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np


def save_coa_to_json(coa_data, material_name):
    """Save CoA data to JSON file for plot functions to read"""
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


def generate_psd_distribution(coa_data):
    """Generate particle size distribution data from D-values"""
    # Extract particle size data
    d_min = coa_data['D_min']
    d10 = coa_data['D10']
    d50 = coa_data['D50']
    d90 = coa_data['D90']
    d_max = coa_data['D_max']
    
    # Create particle size range
    particle_sizes = np.linspace(d_min, d_max, 1000)
    
    # Generate log-normal distribution based on D50 and D90/D10 ratio
    # Using D50 as mean and D90/D10 ratio to estimate standard deviation
    mean_size = d50
    std_size = (d90 - d10) / 4  # Rough estimate of standard deviation
    
    # Generate PDF and CDF
    pdf = stats.norm.pdf(particle_sizes, mean_size, std_size)
    cdf = stats.norm.cdf(particle_sizes, mean_size, std_size)
    
    # Normalize PDF to have area = 1
    pdf = pdf / np.trapz(pdf, particle_sizes)
    
    return particle_sizes, pdf, cdf, mean_size


def create_excel_export(material_name, coa_data=None):
    """Create Excel export data"""
    import io
    
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
    return output.getvalue()
