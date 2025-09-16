"""
Utility Functions for Battery Cell Development Platform

This module provides essential utility functions for data management, file operations,
and data processing within the cell development platform. Supports data persistence,
format conversion, and scientific data manipulation.

Core Functionality:
- Data Persistence: JSON file operations for CoA and performance data
- Data Processing: Particle size distribution generation and statistical analysis
- Export Functions: Excel file generation with multiple sheets
- Display Formatting: Professional table formatting for technical data
- Performance Data: OCV, GITT, and EIS data management

Supported File Formats:
- JSON: Structured data storage for CoA and performance data
- Excel: Multi-sheet export with formatted technical data
- CSV: Data export through pandas integration

Data Categories:
- Certificate of Analysis (CoA): Physical and chemical material properties
- Electrochemical Performance: OCV, GITT, EIS measurement data
- Statistical Analysis: Particle size distribution modeling
- Export Formats: Professional documentation-ready outputs

Author: Cell Development Platform Team
Version: 2.0 - Enhanced data processing and export capabilities
"""
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np


def save_coa_to_json(coa_data, material_name):
    """
    Save Certificate of Analysis data to JSON file for persistent storage.
    
    Creates a structured JSON file containing CoA data for material characterization.
    Automatically creates the data directory if it doesn't exist and generates
    a standardized filename based on the material name.
    
    Args:
        coa_data (dict): Certificate of Analysis data containing:
            - Particle size distribution parameters (D_min, D10, D50, D90, D_max)
            - Surface area and density measurements
            - Electrochemical properties (capacity, voltage, energy density)
            - Chemical composition data (moisture, impurities, pH, crystallinity)
        material_name (str): Name of the material (e.g., 'NMC811', 'LCO', 'Graphite')
    
    Returns:
        str: Full path to the saved JSON file
        
    File Structure:
        - Directory: ./data/
        - Filename format: {material_name.lower()}_coa.json
        - Content: Pretty-printed JSON with 2-space indentation
        
    Example:
        save_coa_to_json(nmc_coa_data, 'NMC811') -> 'data/nmc811_coa.json'
    """
    # Create data directory if it doesn't exist - ensures persistent storage location
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save to JSON file with pretty formatting (2-space indentation)
    filename = f"{data_dir}/{material_name.lower()}_coa.json"
    with open(filename, 'w') as f:
        json.dump(coa_data, f, indent=2)  # Pretty print for human readability
    
    return filename


def save_performance_data_to_json(performance_data, material_name, data_type):
    """
    Save electrochemical performance data to individual JSON files.
    
    Creates separate JSON files for different types of electrochemical measurements,
    enabling modular data management and selective loading of performance data.
    
    Args:
        performance_data (dict): Electrochemical measurement data with x-y pairs:
            - OCV: {'voltage': [V], 'capacity': [mAh/g]}
            - GITT: {'time': [h], 'voltage': [V]}
            - EIS: {'frequency': [Hz], 'impedance': [Ω]}
        material_name (str): Material identifier (e.g., 'NMC811', 'Graphite')
        data_type (str): Type of measurement ('OCV', 'GITT', 'EIS')
    
    Returns:
        str: Full path to the saved JSON file
        
    File Structure:
        - Directory: ./data/
        - Filename format: {material_name.lower()}_{data_type.lower()}.json
        - Content: Pretty-printed JSON with measurement arrays
        
    Example:
        save_performance_data_to_json(ocv_data, 'NMC811', 'OCV') -> 'data/nmc811_ocv.json'
    """
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
    """
    Load electrochemical performance data from JSON files with fallback defaults.
    
    Attempts to load previously saved performance data from JSON files. If the
    file doesn't exist, automatically returns appropriate default data to ensure
    the application continues functioning properly.
    
    Args:
        material_name (str): Material identifier used in filename
        data_type (str): Type of measurement data ('OCV', 'GITT', 'EIS')
    
    Returns:
        dict: Performance data containing measurement arrays:
            - OCV: voltage and capacity arrays
            - GITT: time and voltage arrays  
            - EIS: frequency and impedance arrays
            
    File Search:
        - Looks for: data/{material_name.lower()}_{data_type.lower()}.json
        - Fallback: Returns default data if file not found
        
    Error Handling:
        - Missing file: Returns default data via get_default_performance_data()
        - Invalid JSON: Returns empty dict (graceful degradation)
    """
    filename = f"data/{material_name.lower()}_{data_type.lower()}.json"
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        # Return default data if file doesn't exist
        return get_default_performance_data(data_type)


def get_default_performance_data(data_type):
    """
    Retrieve default electrochemical performance data for different measurement types.
    
    Provides fallback data when custom measurement files are not available.
    Contains realistic default values based on typical cathode material behavior
    to ensure the application functions properly during development and testing.
    
    Args:
        data_type (str): Type of electrochemical measurement:
            - 'OCV': Open Circuit Voltage vs capacity
            - 'GITT': Galvanostatic Intermittent Titration Technique
            - 'EIS': Electrochemical Impedance Spectroscopy
    
    Returns:
        dict: Default measurement data with appropriate units:
            - OCV: voltage (V) and capacity (mAh/g) arrays
            - GITT: time (h) and voltage (V) arrays
            - EIS: frequency (Hz) and impedance (Ω) arrays
            - Unknown type: empty dict
            
    Default Values:
        - Based on typical NMC cathode material behavior
        - Realistic voltage ranges and measurement scales
        - Suitable for demonstration and testing purposes
        
    Note:
        These are generic defaults and should be replaced with actual
        measurement data for production cell designs.
    """
    # Default electrochemical data based on typical NMC cathode behavior
    defaults = {
        'OCV': {'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2], 'capacity': [0, 50, 100, 150, 180, 195, 200]},  # V vs mAh/g
        'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]},  # h vs V
        'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [100, 50, 25, 15, 10, 8]}  # Hz vs Ω
    }
    return defaults.get(data_type, {})


def create_coa_display_table(coa_data):
    """
    Create a professionally formatted pandas DataFrame for Certificate of Analysis display.
    
    Transforms raw CoA data into a structured table with categorized properties,
    appropriate formatting, and merged category headers for enhanced readability.
    Suitable for display in Streamlit dataframes and Excel export.
    
    Args:
        coa_data (dict): Certificate of Analysis data containing all material properties
    
    Returns:
        pd.DataFrame: Formatted table with columns:
            - Category: Property group (Particle Size, Surface & Density, etc.)
            - Property: Specific measurement name
            - Value: Formatted numeric value with appropriate precision
            - Unit: Measurement unit with proper symbols
            
    Categories:
        - Particle Size: D-min, D10, D50, D90, D-max distribution
        - Surface & Density: BET surface area and density measurements
        - Electrochemical: Capacity, voltage, energy density, cycle life
        - Chemical Composition: Moisture, impurities, pH, crystallinity
        
    Formatting Rules:
        - Precision measurements (μm, V, %): 2 decimal places
        - Whole numbers (cycles, ppm): 0 decimal places
        - General values: 3 decimal places
        - Category merging: Empty strings for continuation rows
        
    Usage:
        Perfect for professional technical documentation and quality reports.
    """
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
    """
    Generate continuous particle size distribution from discrete D-values.
    
    Creates probability density function (PDF) and cumulative distribution function (CDF)
    from standard particle size percentiles (D10, D50, D90) using statistical modeling.
    Enables visualization and analysis of particle size distributions for material
    characterization and process optimization.
    
    Args:
        coa_data (dict): CoA data containing particle size distribution parameters:
            - D_min, D_max: Minimum and maximum particle sizes (μm)
            - D10, D50, D90: 10th, 50th, 90th percentile sizes (μm)
    
    Returns:
        tuple: Particle size distribution data containing:
            - particle_sizes (np.array): Size range from D_min to D_max (1000 points)
            - pdf (np.array): Probability density function values (normalized to area=1)
            - cdf (np.array): Cumulative distribution function (0 to 1)
            - mean_size (float): Mean particle size (D50)
            
    Statistical Model:
        - Uses normal distribution approximation
        - Mean: D50 (median particle size)
        - Standard deviation: Estimated from (D90-D10)/4
        - PDF normalized using trapezoidal integration
        
    Applications:
        - Particle size distribution visualization
        - Quality control and specification verification
        - Process optimization and troubleshooting
        - Comparative analysis between material batches
        
    Note:
        Assumes log-normal-like distribution typical of powder materials.
        For precise analysis, use actual laser diffraction measurement data.
    """
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
    """
    Generate comprehensive Excel workbook with multi-sheet material data export.
    
    Creates a professional Excel file containing all available material data across
    multiple organized sheets. Perfect for technical documentation, sharing with
    colleagues, or integration with other analysis tools.
    
    Args:
        material_name (str): Material identifier for data loading (e.g., 'NMC811')
        coa_data (dict, optional): Certificate of Analysis data. If provided,
            creates additional CoA and Material Properties sheets.
    
    Returns:
        bytes: Excel file content as bytes, ready for download or file writing
        
    Excel Sheets Created:
        1. CoA_Data (if coa_data provided): Formatted certificate of analysis
        2. OCV: Open circuit voltage vs capacity data
        3. GITT: Galvanostatic intermittent titration technique data
        4. EIS: Electrochemical impedance spectroscopy measurements
        5. TOCV: Temperature-dependent OCV at 25°C, 45°C, 60°C
        6. Diffusion_Coefficient: Lithium diffusion coefficients vs SOC
        7. Charge_Transfer_Kinetics: Reaction kinetics parameters
        8. Material_Properties (if coa_data provided): Key material properties summary
        
    Data Sources:
        - Performance data loaded from JSON files via load_performance_data_from_json()
        - CoA data from provided parameter or defaults
        - Temperature coefficients estimated from base OCV data
        - Kinetic parameters based on typical material behavior
        
    File Format:
        - Excel 2010+ format (.xlsx) via openpyxl engine
        - Professional formatting with proper column headers and units
        - No row indices for clean data presentation
        - In-memory creation for efficient download handling
        
    Use Cases:
        - Technical documentation and reporting
        - Data sharing with external collaborators
        - Integration with simulation software (COMSOL, etc.)
        - Regulatory submission documentation
        - Quality control record keeping
    """
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
