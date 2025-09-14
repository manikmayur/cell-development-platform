"""
Electrode Materials Module for the Cell Development Platform
Handles binder and conductive agent material libraries
"""
import json
import os
from typing import Dict, List, Optional


class ElectrodeMaterialManager:
    """Manages electrode material libraries for binders and conductive agents"""
    
    def __init__(self):
        self.material_lib_path = "data/electrode_material_lib"
        self._ensure_material_lib_exists()
        
        # Load material libraries
        self.binders = self._load_materials("binders")
        self.conductive_agents = self._load_materials("conductive_agents")
        self.foil_materials = self._load_materials("foil_materials")
    
    def _ensure_material_lib_exists(self):
        """Ensure electrode material library directory exists"""
        if not os.path.exists(self.material_lib_path):
            os.makedirs(self.material_lib_path)
            self._create_default_materials()
    
    def _create_default_materials(self):
        """Create default electrode material libraries"""
        
        # Binders
        binders = {
            "PVDF": {
                "name": "Polyvinylidene Fluoride (PVDF)",
                "type": "binder",
                "properties": {
                    "density": 1.78,  # g/cm³
                    "molecular_weight": 444000,  # g/mol
                    "glass_transition_temp": -35,  # °C
                    "melting_point": 177,  # °C
                    "tensile_strength": 25,  # MPa
                    "elongation_at_break": 300,  # %
                    "solubility": "NMP, DMF",
                    "adhesion_strength": "excellent",
                    "chemical_stability": "excellent"
                },
                "functions": {
                    "viscosity_vs_concentration": {
                        "type": "power_law",
                        "parameters": {"K": 0.1, "n": 0.8},
                        "range": [1, 20]  # wt%
                    },
                    "adhesion_vs_temp": {
                        "type": "exponential_decay",
                        "parameters": {"A": 100, "B": 0.02, "C": 25},
                        "range": [20, 100]  # °C
                    }
                }
            },
            "CMC": {
                "name": "Carboxymethyl Cellulose (CMC)",
                "type": "binder",
                "properties": {
                    "density": 1.59,
                    "molecular_weight": 250000,
                    "glass_transition_temp": 105,
                    "melting_point": 280,
                    "tensile_strength": 15,
                    "elongation_at_break": 50,
                    "solubility": "Water",
                    "adhesion_strength": "good",
                    "chemical_stability": "good"
                },
                "functions": {
                    "viscosity_vs_concentration": {
                        "type": "power_law",
                        "parameters": {"K": 0.05, "n": 1.2},
                        "range": [0.5, 10]
                    }
                }
            },
            "SBR": {
                "name": "Styrene-Butadiene Rubber (SBR)",
                "type": "binder",
                "properties": {
                    "density": 0.94,
                    "molecular_weight": 150000,
                    "glass_transition_temp": -50,
                    "melting_point": 120,
                    "tensile_strength": 20,
                    "elongation_at_break": 500,
                    "solubility": "Water",
                    "adhesion_strength": "excellent",
                    "chemical_stability": "good"
                },
                "functions": {
                    "elastic_modulus_vs_temp": {
                        "type": "linear",
                        "coefficients": [1000, -10],
                        "range": [-50, 100]
                    }
                }
            }
        }
        
        # Conductive Agents
        conductive_agents = {
            "Super_P": {
                "name": "Super P Carbon Black",
                "type": "conductive_agent",
                "properties": {
                    "density": 2.1,  # g/cm³
                    "specific_surface_area": 62,  # m²/g
                    "electrical_conductivity": 100,  # S/cm
                    "particle_size": 40,  # nm
                    "dbp_absorption": 300,  # ml/100g
                    "ash_content": 0.02,  # wt%
                    "moisture_content": 0.5,  # wt%
                    "ph": 7.0
                },
                "functions": {
                    "conductivity_vs_loading": {
                        "type": "percolation",
                        "parameters": {"sigma_0": 0.1, "phi_c": 0.05, "t": 2.0},
                        "range": [0, 20]  # wt%
                    }
                }
            },
            "CNT": {
                "name": "Carbon Nanotubes (CNT)",
                "type": "conductive_agent",
                "properties": {
                    "density": 2.1,
                    "specific_surface_area": 250,
                    "electrical_conductivity": 1000,
                    "particle_size": 10,
                    "aspect_ratio": 1000,
                    "purity": 95,
                    "ash_content": 0.01,
                    "moisture_content": 0.2
                },
                "functions": {
                    "conductivity_vs_loading": {
                        "type": "percolation",
                        "parameters": {"sigma_0": 1.0, "phi_c": 0.01, "t": 1.5},
                        "range": [0, 10]
                    }
                }
            },
            "Graphene": {
                "name": "Graphene",
                "type": "conductive_agent",
                "properties": {
                    "density": 2.2,
                    "specific_surface_area": 2630,
                    "electrical_conductivity": 10000,
                    "particle_size": 5,
                    "layers": 1,
                    "purity": 99,
                    "ash_content": 0.005,
                    "moisture_content": 0.1
                },
                "functions": {
                    "conductivity_vs_loading": {
                        "type": "percolation",
                        "parameters": {"sigma_0": 10.0, "phi_c": 0.005, "t": 1.2},
                        "range": [0, 5]
                    }
                }
            }
        }
        
        # Foil Materials
        foil_materials = {
            "Aluminum": {
                "name": "Aluminum Foil",
                "type": "foil",
                "properties": {
                    "density": 2.7,  # g/cm³
                    "thickness": 20,  # μm
                    "electrical_conductivity": 3.5e7,  # S/m
                    "tensile_strength": 100,  # MPa
                    "elongation": 3,  # %
                    "surface_roughness": 0.5,  # μm
                    "purity": 99.5,  # %
                    "cost": "low"
                },
                "available_thicknesses": [10, 15, 20, 25, 30]  # μm
            },
            "Copper": {
                "name": "Copper Foil",
                "type": "foil",
                "properties": {
                    "density": 8.96,
                    "thickness": 10,
                    "electrical_conductivity": 5.8e7,
                    "tensile_strength": 200,
                    "elongation": 5,
                    "surface_roughness": 0.3,
                    "purity": 99.9,
                    "cost": "medium"
                },
                "available_thicknesses": [6, 8, 10, 12, 15]
            }
        }
        
        # Save materials to JSON files
        self._save_materials("binders", binders)
        self._save_materials("conductive_agents", conductive_agents)
        self._save_materials("foil_materials", foil_materials)
    
    def _save_materials(self, category: str, materials: Dict):
        """Save materials to JSON file"""
        file_path = os.path.join(self.material_lib_path, f"{category}.json")
        with open(file_path, 'w') as f:
            json.dump(materials, f, indent=2)
    
    def _load_materials(self, category: str) -> Dict:
        """Load materials from JSON file"""
        file_path = os.path.join(self.material_lib_path, f"{category}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_binder_options(self) -> List[str]:
        """Get list of available binders"""
        return list(self.binders.keys())
    
    def get_conductive_agent_options(self) -> List[str]:
        """Get list of available conductive agents"""
        return list(self.conductive_agents.keys())
    
    def get_foil_material_options(self) -> List[str]:
        """Get list of available foil materials"""
        return list(self.foil_materials.keys())
    
    def get_binder_properties(self, binder_name: str) -> Dict:
        """Get properties for a specific binder"""
        return self.binders.get(binder_name, {})
    
    def get_conductive_agent_properties(self, agent_name: str) -> Dict:
        """Get properties for a specific conductive agent"""
        return self.conductive_agents.get(agent_name, {})
    
    def get_foil_material_properties(self, foil_name: str) -> Dict:
        """Get properties for a specific foil material"""
        return self.foil_materials.get(foil_name, {})
    
    def calculate_electrode_properties(self, composition: Dict) -> Dict:
        """Calculate electrode properties based on composition"""
        # Extract composition
        active_material_wt = composition.get('active_material_wt', 0)
        binder_wt = composition.get('binder_wt', 0)
        conductive_wt = composition.get('conductive_wt', 0)
        foil_thickness = composition.get('foil_thickness', 20)  # μm
        
        # Get material densities
        active_density = composition.get('active_material_density', 4.7)  # g/cm³
        binder_density = composition.get('binder_density', 1.78)
        conductive_density = composition.get('conductive_density', 2.1)
        foil_density = composition.get('foil_density', 2.7)
        
        # Calculate mass fractions
        total_wt = active_material_wt + binder_wt + conductive_wt
        if total_wt == 0:
            return {}
        
        active_vol_frac = (active_material_wt / active_density) / (
            (active_material_wt / active_density) + 
            (binder_wt / binder_density) + 
            (conductive_wt / conductive_density)
        )
        
        binder_vol_frac = (binder_wt / binder_density) / (
            (active_material_wt / active_density) + 
            (binder_wt / binder_density) + 
            (conductive_wt / conductive_density)
        )
        
        conductive_vol_frac = (conductive_wt / conductive_density) / (
            (active_material_wt / active_density) + 
            (binder_wt / binder_density) + 
            (conductive_wt / conductive_density)
        )
        
        # Calculate electrode density
        electrode_density = (
            active_vol_frac * active_density +
            binder_vol_frac * binder_density +
            conductive_vol_frac * conductive_density
        )
        
        # Calculate porosity (assuming 40% porosity for typical electrode)
        porosity = 0.4  # This could be calculated based on particle packing
        
        # Calculate mass loading (mg/cm²)
        # Assuming electrode thickness of 100 μm
        electrode_thickness = 100  # μm
        mass_loading = electrode_density * electrode_thickness * 0.1  # mg/cm²
        
        # Calculate calendared thickness
        calendared_thickness = electrode_thickness * (1 - porosity)
        
        return {
            'porosity': porosity * 100,  # %
            'mass_loading': mass_loading,  # mg/cm²
            'calendared_thickness': calendared_thickness,  # μm
            'electrode_density': electrode_density,  # g/cm³
            'active_vol_frac': active_vol_frac * 100,  # %
            'binder_vol_frac': binder_vol_frac * 100,  # %
            'conductive_vol_frac': conductive_vol_frac * 100  # %
        }
