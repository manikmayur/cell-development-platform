"""
Material Data Repository for Battery Cell Development Platform

This module provides comprehensive default material data for cathode and anode
materials used in lithium-ion battery cells. Contains Certificate of Analysis (CoA)
data, performance characteristics, and electrochemical properties.

Supported Materials:
Cathode Materials:
- NMC811 (LiNi0.8Mn0.1Co0.1O2): High energy density nickel-rich cathode
- LCO (LiCoO2): Traditional cobalt-based cathode material
- NCA (LiNi0.8Co0.15Al0.05O2): Aluminum-doped nickel cobalt cathode

Anode Materials:
- Graphite (C): Standard carbon-based anode material
- Silicon (Si): High capacity silicon anode with volume expansion challenges
- Tin (Sn): Alternative high capacity metallic anode material

Data Categories:
- Physical Properties: Particle size distribution, surface area, densities
- Electrochemical Properties: Capacity, voltage, energy density, cycle life
- Chemical Properties: Moisture content, impurities, pH, crystallinity
- Performance Data: OCV curves, GITT profiles, EIS measurements
- Cycle Performance: Capacity retention and coulombic efficiency over time

Author: Cell Development Platform Team
Version: 2.0 - Enhanced multi-material support
"""

def get_default_material_data(material_name):
    """
    Retrieve comprehensive default data for cathode materials.
    
    Returns complete material characterization data including physical properties,
    electrochemical performance, and cycle life data for cathode materials.
    Provides realistic default values based on literature and industry standards.
    
    Args:
        material_name (str): Name of the cathode material. Supported options:
            - 'NMC811': High energy density nickel-rich cathode
            - 'LCO': Traditional lithium cobalt oxide
            - 'NCA': Aluminum-doped nickel cobalt cathode
    
    Returns:
        dict: Complete material data containing:
            - name (str): Full chemical name and formula
            - coa_data (dict): Certificate of Analysis data including:
                * Particle size distribution (D_min, D10, D50, D90, D_max) in μm
                * Surface properties (BET surface area in m²/g)
                * Density measurements (tap, bulk, true) in g/cm³
                * Electrochemical properties (capacity in mAh/g, voltage in V)
                * Impurity and physical characteristics
            - performance_data (dict): Electrochemical test data:
                * OCV: Open circuit voltage vs capacity curves
                * GITT: Galvanostatic intermittent titration data
                * EIS: Electrochemical impedance spectroscopy results
            - cycle_life (dict): Long-term cycling performance data
            - coulombic_efficiency (dict): Charge/discharge efficiency over cycles
    
    Note:
        If an unknown material name is provided, defaults to NMC811 data.
        All data represents typical values and should be validated with
        actual material certificates for production use.
    """
    # Comprehensive cathode material database with realistic commercial-grade specifications
    default_data = {
        'NMC811': {  # High energy density nickel-rich cathode (80% Ni, 10% Mn, 10% Co)
            'name': 'NMC811 (LiNi0.8Mn0.1Co0.1O2)',
            'coa_data': {
                # Particle size distribution (μm) - fine powder for good mixing
                'D_min': 0.5, 'D10': 2.1, 'D50': 8.5, 'D90': 18.2, 'D_max': 45.0,
                # Surface area and density properties
                'BET': 0.8, 'tap_density': 2.4, 'bulk_density': 1.8, 'true_density': 4.7,  # m²/g, g/cm³
                # Electrochemical performance characteristics
                'capacity': 200, 'voltage': 3.8, 'energy_density': 760, 'cycle_life': 1000,  # mAh/g, V, Wh/kg, cycles
                # Chemical purity and physical properties
                'moisture': 0.02, 'impurities': 50, 'pH': 11.5, 'crystallinity': 98.5  # %, ppm, -, %
            },
            'performance_data': {  # Electrochemical characterization data
                # Open Circuit Voltage curve (V vs mAh/g) - charge profile
                'OCV': {'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2], 'capacity': [0, 50, 100, 150, 180, 195, 200]},
                # Galvanostatic Intermittent Titration Technique (h vs V)
                'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]},
                # Electrochemical Impedance Spectroscopy (Hz vs Ohm)
                'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [100, 50, 25, 15, 10, 8]}
            },
            # Long-term cycling performance data
            'cycle_life': {'cycles': list(range(0, 1001, 50)), 'capacity_retention': [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60]},  # cycles vs %
            'coulombic_efficiency': {'cycles': list(range(0, 1001, 50)), 'efficiency': [99.5, 99.6, 99.7, 99.8, 99.9, 99.9, 99.8, 99.7, 99.6, 99.5, 99.4, 99.3, 99.2, 99.1, 99.0, 98.9, 98.8, 98.7, 98.6, 98.5, 98.4]}  # cycles vs %
        },
        'LCO': {  # Traditional lithium cobalt oxide cathode - high voltage, moderate capacity
            'name': 'LCO (LiCoO2)',
            'coa_data': {
                'D_min': 0.3, 'D10': 1.8, 'D50': 6.2, 'D90': 15.0, 'D_max': 35.0,
                'BET': 1.2, 'tap_density': 2.6, 'bulk_density': 2.0, 'true_density': 5.1,
                'capacity': 140, 'voltage': 3.9, 'energy_density': 546, 'cycle_life': 500,
                'moisture': 0.015, 'impurities': 30, 'pH': 11.8, 'crystallinity': 99.2
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
                'D_min': 0.4, 'D10': 2.0, 'D50': 7.8, 'D90': 16.5, 'D_max': 40.0,
                'BET': 0.9, 'tap_density': 2.3, 'bulk_density': 1.7, 'true_density': 4.6,
                'capacity': 190, 'voltage': 3.7, 'energy_density': 703, 'cycle_life': 800,
                'moisture': 0.018, 'impurities': 40, 'pH': 11.2, 'crystallinity': 98.8
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
    return default_data.get(material_name, default_data['NMC811'])


def get_default_anode_data(material_name):
    """
    Retrieve comprehensive default data for anode materials.
    
    Returns complete material characterization data including physical properties
    and electrochemical performance for anode materials. Provides realistic
    default values based on literature and industry standards.
    
    Args:
        material_name (str): Name of the anode material. Supported options:
            - 'Graphite': Standard carbon-based anode (372 mAh/g capacity)
            - 'Silicon': High capacity silicon anode (4200 mAh/g, volume expansion)
            - 'Tin': Alternative metallic anode (994 mAh/g capacity)
    
    Returns:
        dict: Complete anode material data containing:
            - name (str): Full material name and chemical symbol
            - coa_data (dict): Certificate of Analysis data including:
                * Particle size distribution (D_min, D10, D50, D90, D_max) in μm
                * Surface properties (BET surface area in m²/g)
                * Density measurements (tap, bulk, true) in g/cm³
                * Electrochemical properties (capacity in mAh/g, voltage in V)
                * Moisture content, impurities, pH, and crystallinity
            - performance_data (dict): Electrochemical characterization:
                * OCV: Open circuit voltage vs capacity profiles
                * GITT: Galvanostatic intermittent titration curves
                * EIS: Electrochemical impedance spectroscopy data
    
    Note:
        Silicon and tin anodes show high theoretical capacities but face
        challenges with volume expansion during cycling. Graphite provides
        stable cycling with moderate capacity. Defaults to graphite data
        for unknown material names.
    """
    # Comprehensive anode material database with performance trade-offs
    default_data = {
        'Graphite': {  # Standard carbon anode - stable, moderate capacity, excellent cycling
            'name': 'Graphite (C)',
            'coa_data': {
                # Particle size distribution (μm) - larger particles than cathode
                'D_min': 5.0, 'D10': 8.2, 'D50': 15.5, 'D90': 28.0, 'D_max': 50.0,
                # Surface area and density properties
                'BET': 2.5, 'tap_density': 1.0, 'bulk_density': 0.8, 'true_density': 2.2,  # m²/g, g/cm³
                # Electrochemical properties - stable low voltage operation
                'capacity': 372, 'voltage': 0.1, 'energy_density': 37, 'cycle_life': 2000,  # mAh/g, V, Wh/kg, cycles
                # Chemical properties - low moisture sensitivity
                'moisture': 0.01, 'impurities': 20, 'pH': 7.0, 'crystallinity': 95.0  # %, ppm, -, %
            },
            'performance_data': {
                'OCV': {'voltage': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35], 'capacity': [0, 60, 120, 180, 240, 300, 372]},
                'GITT': {'time': [0, 1, 2, 3, 4, 5], 'voltage': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]},
                'EIS': {'frequency': [0.01, 0.1, 1, 10, 100, 1000], 'impedance': [50, 25, 12, 8, 5, 3]}
            }
        },
        'Silicon': {  # High capacity silicon anode - extreme capacity but volume expansion challenges
            'name': 'Silicon (Si)',
            'coa_data': {
                # Fine particle size distribution (μm) - nano-scale to mitigate expansion
                'D_min': 1.0, 'D10': 2.5, 'D50': 5.0, 'D90': 10.0, 'D_max': 20.0,
                # High surface area, low density due to nanostructuring
                'BET': 15.0, 'tap_density': 0.8, 'bulk_density': 0.6, 'true_density': 2.3,  # m²/g, g/cm³
                # Ultra-high capacity but shorter cycle life due to volume expansion
                'capacity': 4200, 'voltage': 0.4, 'energy_density': 1680, 'cycle_life': 500,  # mAh/g, V, Wh/kg, cycles
                # Strict moisture control required
                'moisture': 0.005, 'impurities': 100, 'pH': 7.5, 'crystallinity': 90.0  # %, ppm, -, %
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


def get_default_coa_data(material_name):
    """
    Retrieve Certificate of Analysis (CoA) data for cathode materials.
    
    Returns standardized CoA data including physical, chemical, and electrochemical
    properties typically found on material supplier certificates. This data is
    essential for electrode design calculations and quality control.
    
    Args:
        material_name (str): Cathode material name ('NMC811', 'LCO', 'NCA')
    
    Returns:
        dict: Certificate of Analysis data containing:
            - Particle Size Distribution:
                * D_min, D_max (μm): Minimum and maximum particle sizes
                * D10, D50, D90 (μm): 10th, 50th, 90th percentile sizes
            - Surface and Density Properties:
                * BET (m²/g): Specific surface area by Brunauer-Emmett-Teller method
                * tap_density (g/cm³): Density after tapping/compaction
                * bulk_density (g/cm³): Loose powder density
                * true_density (g/cm³): Theoretical material density
            - Electrochemical Properties:
                * capacity (mAh/g): Specific capacity at standard conditions
                * voltage (V): Average operating voltage vs Li/Li+
                * energy_density (Wh/kg): Specific energy density
                * cycle_life (cycles): Expected cycle life under standard conditions
            - Chemical Analysis:
                * moisture (%): Water content by Karl Fischer titration
                * impurities (ppm): Total impurity content
                * pH: Slurry pH measurement
                * crystallinity (%): X-ray diffraction crystalline fraction
    
    Note:
        Defaults to NMC811 data for unrecognized material names.
        Values represent typical commercial-grade material specifications.
    """
    default_data = {
        'NMC811': {
            'D_min': 0.5, 'D10': 2.1, 'D50': 8.5, 'D90': 18.2, 'D_max': 45.0,
            'BET': 0.8, 'tap_density': 2.4, 'bulk_density': 1.8, 'true_density': 4.7,
            'capacity': 200, 'voltage': 3.8, 'energy_density': 760, 'cycle_life': 1000,
            'moisture': 0.02, 'impurities': 50, 'pH': 11.5, 'crystallinity': 98.5
        },
        'LCO': {
            'D_min': 0.3, 'D10': 1.8, 'D50': 6.2, 'D90': 15.0, 'D_max': 35.0,
            'BET': 1.2, 'tap_density': 2.6, 'bulk_density': 2.0, 'true_density': 5.1,
            'capacity': 140, 'voltage': 3.9, 'energy_density': 546, 'cycle_life': 500,
            'moisture': 0.015, 'impurities': 30, 'pH': 11.8, 'crystallinity': 99.2
        },
        'NCA': {
            'D_min': 0.4, 'D10': 2.0, 'D50': 7.8, 'D90': 16.5, 'D_max': 40.0,
            'BET': 0.9, 'tap_density': 2.3, 'bulk_density': 1.7, 'true_density': 4.6,
            'capacity': 190, 'voltage': 3.7, 'energy_density': 703, 'cycle_life': 800,
            'moisture': 0.018, 'impurities': 40, 'pH': 11.2, 'crystallinity': 98.8
        }
    }
    return default_data.get(material_name, default_data['NMC811'])
