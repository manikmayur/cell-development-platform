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

# Import required modules for file operations
import json
import os
from typing import Dict, List, Optional


def load_material_from_file(material_name: str, category: str) -> Optional[Dict]:
    """
    Load material data from JSON file based on material name and category.
    
    Args:
        material_name (str): Name of the material (e.g., 'NMC811', 'Graphite')
        category (str): Material category ('cathodes', 'anodes', 'binders')
        
    Returns:
        dict: Material data from JSON file, or None if file doesn't exist
    """
    file_path = f"data/materials/{category}/{material_name}.json"
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading material file {file_path}: {e}")
            return None
    return None


def get_available_materials(category: str) -> List[str]:
    """
    Get list of available materials from a specific category directory.
    
    Args:
        category (str): Material category ('cathodes', 'anodes', 'binders')
        
    Returns:
        list: List of available material names (without .json extension)
    """
    materials_dir = f"data/materials/{category}"
    
    if not os.path.exists(materials_dir):
        return []
        
    try:
        files = os.listdir(materials_dir)
        # Filter for JSON files and remove extension
        materials = [f[:-5] for f in files if f.endswith('.json')]
        return sorted(materials)
    except OSError as e:
        print(f"Error reading materials directory {materials_dir}: {e}")
        return []


def get_all_materials() -> Dict[str, List[str]]:
    """
    Get all available materials organized by category.
    
    Returns:
        dict: Dictionary with categories as keys and lists of materials as values
    """
    categories = ['cathodes', 'anodes', 'binders', 'casings', 'foils', 'electrolytes', 'separators']
    all_materials = {}
    
    for category in categories:
        all_materials[category] = get_available_materials(category)
    
    return all_materials


def get_default_material_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for cathode materials from JSON files.
    
    This function maintains backwards compatibility by automatically loading
    cathode material data from the JSON file system.
    
    Args:
        material_name (str): Name of the cathode material (e.g., 'NMC811', 'LCO', 'NCA')
    
    Returns:
        dict: Complete material data from JSON file, or None if not found
        
    Note:
        This function now loads data from JSON files in data/materials/cathodes/
        instead of using hardcoded data. Maintains same return structure for
        backwards compatibility.
    """
    return load_material_from_file(material_name, 'cathodes')


def get_default_anode_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for anode materials from JSON files.
    
    This function maintains backwards compatibility by automatically loading
    anode material data from the JSON file system.
    
    Args:
        material_name (str): Name of the anode material (e.g., 'Graphite', 'Silicon', 'Tin')
    
    Returns:
        dict: Complete anode material data from JSON file, or None if not found
        
    Note:
        This function now loads data from JSON files in data/materials/anodes/
        instead of using hardcoded data. Maintains same return structure for
        backwards compatibility.
    """
    return load_material_from_file(material_name, 'anodes')


def get_default_binder_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for binder materials from JSON files.
    
    Args:
        material_name (str): Name of the binder material (e.g., 'PVDF', 'CMC', 'SBR')
    
    Returns:
        dict: Complete binder material data from JSON file, or None if not found
    """
    return load_material_from_file(material_name, 'binders')


def get_default_casing_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for casing materials from JSON files.
    
    Args:
        material_name (str): Name of the casing material (e.g., 'Aluminum_3003', 'Steel_316L')
    
    Returns:
        dict: Complete casing material data from JSON file, or None if not found
    """
    return load_material_from_file(material_name, 'casings')


def get_default_foil_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for foil materials from JSON files.
    
    Args:
        material_name (str): Name of the foil material (e.g., 'Aluminum_Foil', 'Copper_Foil')
    
    Returns:
        dict: Complete foil material data from JSON file, or None if not found
    """
    return load_material_from_file(material_name, 'foils')


def get_default_electrolyte_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for electrolyte materials from JSON files.
    
    Args:
        material_name (str): Name of the electrolyte (e.g., 'LiPF6_EC_DMC', 'LiTFSI_EC_DMC')
    
    Returns:
        dict: Complete electrolyte material data from JSON file, or None if not found
    """
    return load_material_from_file(material_name, 'electrolytes')


def get_default_separator_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive material data for separator materials from JSON files.
    
    Args:
        material_name (str): Name of the separator (e.g., 'PE', 'PP', 'PE_PP_Trilayer')
    
    Returns:
        dict: Complete separator material data from JSON file, or None if not found
    """
    return load_material_from_file(material_name, 'separators')


def get_default_coa_data(material_name: str) -> Optional[Dict]:
    """
    Retrieve Certificate of Analysis (CoA) data for cathode materials from JSON files.
    
    This function maintains backwards compatibility by loading CoA data from
    the cathode material JSON files.
    
    Args:
        material_name (str): Cathode material name (e.g., 'NMC811', 'LCO', 'NCA')
    
    Returns:
        dict: Certificate of Analysis data from JSON file, or None if not found
        
    Note:
        This function now extracts CoA data from JSON files instead of using
        hardcoded data. Returns the 'coa_data' section from the material file.
    """
    material_data = load_material_from_file(material_name, 'cathodes')
    if material_data and 'coa_data' in material_data:
        return material_data['coa_data']
    return None
