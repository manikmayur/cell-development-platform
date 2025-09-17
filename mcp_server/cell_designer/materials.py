from typing import Optional, Dict, Union
from pydantic import BaseModel, ConfigDict, Field

# Material aliases for external search and identification
MATERIAL_ALIASES: Dict[str, list] = {
    "Aluminum-Laminate": ["Al-Laminate", "Al-Lam", "Aluminum Laminate", "Al Laminate", "Al-L", "AL"],
    "Copper": ["Cu", "Copper metal", "Copper foil", "Cu foil", "Copper sheet"],
    "Aluminum": ["Al", "Aluminum metal", "Aluminum foil", "Al foil", "Al sheet", "Aluminum sheet"],
    "Steel": ["Carbon steel", "Mild steel", "Low carbon steel", "Steel alloy", "Steel sheet"],
    "Stainless Steel": ["SS", "Stainless", "Stainless steel alloy", "SS sheet", "Corrosion resistant steel"],
    "Nickel": ["Ni", "Nickel metal", "Nickel foil", "Ni foil", "Nickel sheet"],
    "Titanium": ["Ti", "Titanium metal", "Titanium alloy", "Ti alloy", "Titanium sheet"],
    "Silicon": ["Si", "Silicon metal", "Silicon powder", "Si powder", "Silicon anode"],
    "Graphite": ["C", "Carbon graphite", "Graphite powder", "Graphite anode", "Natural graphite", "Synthetic graphite"],
    "NMC811": ["NMC", "NMC811", "LiNi0.8Mn0.1Co0.1O2", "NMC-811"],
    "LFP": ["Lithium Iron Phosphate", "LiFePO4", "LFP cathode", "Iron phosphate", "LiFePO4 cathode"],
    "LCO": ["Lithium Cobalt Oxide", "LiCoO2", "LCO cathode", "Cobalt oxide", "LiCoO2 cathode"],
    "NCA": ["Nickel Cobalt Aluminum", "LiNi0.8Co0.15Al0.05O2", "NCA cathode", "Aluminum doped NCA"],
    "LTO": ["Lithium Titanate", "Li4Ti5O12", "LTO anode", "Titanate anode", "Li4Ti5O12 anode"],
    "PVDF": ["Polyvinylidene fluoride", "Polyvinylidene difluoride", "PVDF binder", "PVDF polymer", "Kynar"],
    "Carbon": ["C", "Carbon black", "Carbon powder", "Carbon additive", "Carbon conductive agent", "CNT"],
    "CMC": ["Carboxymethyl cellulose", "Sodium CMC", "CMC binder", "Cellulose derivative", "CMC thickener"],
    "SBR": ["Styrene butadiene rubber", "SBR binder", "Styrene butadiene", "SBR latex", "SBR emulsion"],
    # Sodium-ion battery materials
    "Sodium": ["Na", "Sodium metal", "Na metal", "Sodium anode", "Na anode", "Sodium foil"],
    "NaFePO4": ["Sodium Iron Phosphate", "SFP", "NaFePO4 cathode", "Sodium iron phosphate", "SFP cathode"],
    "Na3V2(PO4)3": ["Sodium Vanadium Phosphate", "NVP", "Na3V2(PO4)3 cathode", "NVP cathode", "Sodium vanadium phosphate"],
    "Na2Fe2(SO4)3": ["Sodium Iron Sulfate", "NFS", "Na2Fe2(SO4)3 cathode", "NFS cathode", "Sodium iron sulfate"],
    "NaCrO2": ["Sodium Chromium Oxide", "NCO", "NaCrO2 cathode", "NCO cathode", "Sodium chromium oxide"],
    "NaMnO2": ["Sodium Manganese Oxide", "NMO", "NaMnO2 cathode", "NMO cathode", "Sodium manganese oxide"],
    "NaNiO2": ["Sodium Nickel Oxide", "NNO", "NaNiO2 cathode", "NNO cathode", "Sodium nickel oxide"],
    "NaCoO2": ["Sodium Cobalt Oxide", "NCO", "NaCoO2 cathode", "NCO cathode", "Sodium cobalt oxide"],
    "NaTi2(PO4)3": ["Sodium Titanium Phosphate", "NTP", "NaTi2(PO4)3 anode", "NTP anode", "Sodium titanium phosphate"],
    "Na2Ti3O7": ["Sodium Titanium Oxide", "NTO", "Na2Ti3O7 anode", "NTO anode", "Sodium titanium oxide"],
    "Hard Carbon": ["Hard carbon", "Hard carbon anode", "Hard carbon sodium", "Hard carbon Na", "Hard carbon sodium-ion"],
    "Soft Carbon": ["Soft carbon", "Soft carbon anode", "Soft carbon sodium", "Soft carbon Na", "Soft carbon sodium-ion"],
    # Lithium metal materials
    "Lithium": ["Li", "Lithium metal", "Li metal", "Lithium anode", "Li anode", "Lithium foil", "Lithium sheet"],
    "Lithium Metal": ["Li metal", "Lithium metal", "Li anode", "Lithium anode", "Lithium foil", "Li foil"],
    # Additional sodium-ion specific materials
    "NaPF6": ["Sodium Hexafluorophosphate", "NaPF6 electrolyte", "Sodium PF6", "NaPF6 salt", "Sodium hexafluorophosphate"],
    "NaClO4": ["Sodium Perchlorate", "NaClO4 electrolyte", "Sodium perchlorate", "NaClO4 salt"],
    "NaBF4": ["Sodium Tetrafluoroborate", "NaBF4 electrolyte", "Sodium tetrafluoroborate", "NaBF4 salt"],
    "NaTFSI": ["Sodium Trifluoromethanesulfonimide", "NaTFSI electrolyte", "Sodium TFSI", "NaTFSI salt", "Sodium trifluoromethanesulfonimide"],
    "NaFSI": ["Sodium Bis(fluorosulfonyl)imide", "NaFSI electrolyte", "Sodium FSI", "NaFSI salt", "Sodium bis(fluorosulfonyl)imide"]
}

# Reverse alias mapping for quick lookup
REVERSE_ALIASES: Dict[str, str] = {}
for material_name, aliases in MATERIAL_ALIASES.items():
    for alias in aliases:
        REVERSE_ALIASES[alias.lower()] = material_name
        REVERSE_ALIASES[alias.upper()] = material_name
        REVERSE_ALIASES[alias] = material_name

def find_material_by_alias(alias: str) -> Optional[str]:
    """
    Find a material by its alias, acronym, or alternative name.
    
    Args:
        alias (str): The alias, acronym, or alternative name to search for
        
    Returns:
        Optional[str]: The canonical material name if found, None otherwise
        
    Examples:
        >>> find_material_by_alias("Cu")
        "Copper"
        >>> find_material_by_alias("LiFePO4")
        "LFP"
        >>> find_material_by_alias("carbon black")
        "Carbon"
    """
    # Direct lookup
    if alias in REVERSE_ALIASES:
        return REVERSE_ALIASES[alias]
    
    # Case-insensitive lookup
    alias_lower = alias.lower()
    if alias_lower in REVERSE_ALIASES:
        return REVERSE_ALIASES[alias_lower]
    
    # Check if it's a direct material name
    if alias in KNOWN_MATERIALS:
        return alias
    
    # Only do partial matching for longer strings to avoid false positives
    if len(alias) > 2:
        # Partial match lookup with more strict criteria
        for canonical_name, aliases in MATERIAL_ALIASES.items():
            # Check if the alias is contained in any of the material aliases
            for material_alias in aliases:
                material_alias_lower = material_alias.lower()
                # Only match if the alias is a significant part of the material alias
                if (alias_lower in material_alias_lower and 
                    len(alias_lower) >= 3 and  # Minimum length for partial matches
                    (material_alias_lower.startswith(alias_lower) or 
                     material_alias_lower.endswith(alias_lower) or
                     f" {alias_lower} " in f" {material_alias_lower} ")):  # Word boundary matching
                    return canonical_name
    
    return None

def search_materials(query: str) -> Dict[str, list]:
    """
    Search for materials by query string, returning matches with relevance scores.
    
    Args:
        query (str): Search query string
        
    Returns:
        Dict[str, list]: Dictionary with material names as keys and lists of matching aliases as values
        
    Examples:
        >>> search_materials("copper")
        {"Copper": ["Cu", "Copper metal", "Copper foil"]}
        >>> search_materials("cathode")
        {"NMC811": ["NMC811 cathode"], "LFP": ["LFP cathode"], "LCO": ["LCO cathode"], "NCA": ["NCA cathode"]}
    """
    query_lower = query.lower()
    results = {}
    
    for material_name, aliases in MATERIAL_ALIASES.items():
        matches = []
        
        # Check material name (exact match or starts with query)
        if query_lower == material_name.lower() or material_name.lower().startswith(query_lower):
            matches.append(material_name)
        
        # Check aliases for more relevant matches
        for alias in aliases:
            alias_lower = alias.lower()
            # Only include matches that are meaningful (not just partial word matches)
            if (query_lower == alias_lower or 
                alias_lower.startswith(query_lower) or 
                (query_lower in alias_lower and len(query_lower) > 2)):  # Avoid very short partial matches
                matches.append(alias)
        
        if matches:
            results[material_name] = matches
    
    return results

def get_material_aliases(material_name: str) -> Optional[list]:
    """
    Get all aliases for a given material name.
    
    Args:
        material_name (str): The canonical material name
        
    Returns:
        Optional[list]: List of aliases if material exists, None otherwise
        
    Examples:
        >>> get_material_aliases("Copper")
        ["Cu", "Copper metal", "Copper foil", "Cu foil", "Copper sheet"]
    """
    return MATERIAL_ALIASES.get(material_name)

def list_all_materials() -> Dict[str, list]:
    """
    Get all materials with their aliases.
    
    Returns:
        Dict[str, list]: Dictionary of all materials with their aliases
    """
    return MATERIAL_ALIASES.copy()

def validate_material_input(material_input: str) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Validate material input and return validation status, canonical name, and any error message.
    
    Args:
        material_input (str): The material input to validate
        
    Returns:
        tuple[bool, Optional[str], Optional[str]]: (is_valid, canonical_name, error_message)
        
    Examples:
        >>> validate_material_input("Cu")
        (True, "Copper", None)
        >>> validate_material_input("unknown_material")
        (False, None, "Unknown material: unknown_material")
    """
    canonical_name = find_material_by_alias(material_input)
    
    if canonical_name:
        return True, canonical_name, None
    else:
        return False, None, f"Unknown material: {material_input}. Available materials: {list(KNOWN_MATERIALS.keys())}"

# Predefined material property database with units
KNOWN_MATERIALS: dict = {
    "Aluminum-Laminate": {
        "Name": "Aluminum-Laminate",
        "Density [g.cm-3]": 2.7,
        "Electrical conductivity [S.m-1]": 3.77e7,
        "Thermal conductivity [W.m-1.K-1]": 237,
        "Specific heat [J.g-1.K-1]": 0.897,
    },
    "Copper": {
        "Name": "Copper",
        "Density [g.cm-3]": 8.96,
        "Electrical conductivity [S.m-1]": 5.96e7,
        "Thermal conductivity [W.m-1.K-1]": 401,
        "Specific heat [J.g-1.K-1]": 0.385,
    },
    "Aluminum": {
        "Name": "Aluminum",
        "Density [g.cm-3]": 2.70,
        "Electrical conductivity [S.m-1]": 3.77e7,
        "Thermal conductivity [W.m-1.K-1]": 237,
        "Specific heat [J.g-1.K-1]": 0.897,
    },
    "Steel": {
        "Name": "Steel",
        "Density [g.cm-3]": 7.85,
        "Electrical conductivity [S.m-1]": 1.45e6,
        "Thermal conductivity [W.m-1.K-1]": 50.2,
        "Specific heat [J.g-1.K-1]": 0.49,
    },
    "Stainless Steel": {
        "Name": "Stainless Steel",
        "Density [g.cm-3]": 8.00,
        "Electrical conductivity [S.m-1]": 1.45e6,
        "Thermal conductivity [W.m-1.K-1]": 16.2,
        "Specific heat [J.g-1.K-1]": 0.50,
    },
    "Nickel": {
        "Name": "Nickel",
        "Density [g.cm-3]": 8.90,
        "Electrical conductivity [S.m-1]": 1.43e7,
        "Thermal conductivity [W.m-1.K-1]": 90.9,
        "Specific heat [J.g-1.K-1]": 0.444,
    },
    "Titanium": {
        "Name": "Titanium",
        "Density [g.cm-3]": 4.51,
        "Electrical conductivity [S.m-1]": 2.38e6,
        "Thermal conductivity [W.m-1.K-1]": 21.9,
        "Specific heat [J.g-1.K-1]": 0.523,
    },
    "Silicon": {
        "Name": "Silicon",
        "Density [g.cm-3]": 2.33,
        "Electrical conductivity [S.m-1]": 1e3,
        "Thermal conductivity [W.m-1.K-1]": 149,
        "Specific heat [J.g-1.K-1]": 0.71,
    },
    "Graphite": {
        "Name": "Graphite",
        "Density [g.cm-3]": 2.26,
        "Electrical conductivity [S.m-1]": 1e5,
        "Thermal conductivity [W.m-1.K-1]": 120,
        "Specific heat [J.g-1.K-1]": 0.71,
    },
    "NMC811": {
        "Name": "NMC811",
        "Density [g.cm-3]": 4.8,
        "Electrical conductivity [S.m-1]": 1.0,
        "Thermal conductivity [W.m-1.K-1]": 2.5,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "LFP": {
        "Name": "LFP",
        "Density [g.cm-3]": 3.6,
        "Electrical conductivity [S.m-1]": 1e-6,
        "Thermal conductivity [W.m-1.K-1]": 1.5,
        "Specific heat [J.g-1.K-1]": 0.7,
    },
    "LCO": {
        "Name": "LCO",
        "Density [g.cm-3]": 5.1,
        "Electrical conductivity [S.m-1]": 1e-4,
        "Thermal conductivity [W.m-1.K-1]": 3.7,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "NCA": {
        "Name": "NCA",
        "Density [g.cm-3]": 4.8,
        "Electrical conductivity [S.m-1]": 1.0,
        "Thermal conductivity [W.m-1.K-1]": 2.5,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "LTO": {
        "Name": "LTO",
        "Density [g.cm-3]": 3.5,
        "Electrical conductivity [S.m-1]": 1e-7,
        "Thermal conductivity [W.m-1.K-1]": 1.0,
        "Specific heat [J.g-1.K-1]": 0.7,
    },
    "PVDF": {
        "Name": "PVDF",
        "Density [g.cm-3]": 1.78,
        "Electrical conductivity [S.m-1]": 1e-16,
        "Thermal conductivity [W.m-1.K-1]": 0.19,
        "Specific heat [J.g-1.K-1]": 1.2,
    },
    "Carbon": {
        "Name": "Carbon",
        "Density [g.cm-3]": 2.2,
        "Electrical conductivity [S.m-1]": 1e4,
        "Thermal conductivity [W.m-1.K-1]": 140,
        "Specific heat [J.g-1.K-1]": 0.71,
    },
    "CMC": {
        "Name": "CMC",
        "Density [g.cm-3]": 1.6,
        "Electrical conductivity [S.m-1]": 1e-10,
        "Thermal conductivity [W.m-1.K-1]": 0.2,
        "Specific heat [J.g-1.K-1]": 1.2,
    },
    "SBR": {
        "Name": "SBR",
        "Density [g.cm-3]": 0.94,
        "Electrical conductivity [S.m-1]": 1e-12,
        "Thermal conductivity [W.m-1.K-1]": 0.13,
        "Specific heat [J.g-1.K-1]": 1.7,
    },
    # Sodium-ion battery materials
    "Sodium": {
        "Name": "Sodium",
        "Density [g.cm-3]": 0.97,
        "Electrical conductivity [S.m-1]": 2.1e7,
        "Thermal conductivity [W.m-1.K-1]": 142,
        "Specific heat [J.g-1.K-1]": 1.23,
    },
    "NaFePO4": {
        "Name": "NaFePO4",
        "Density [g.cm-3]": 3.4,
        "Electrical conductivity [S.m-1]": 1e-8,
        "Thermal conductivity [W.m-1.K-1]": 1.2,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "Na3V2(PO4)3": {
        "Name": "Na3V2(PO4)3",
        "Density [g.cm-3]": 3.2,
        "Electrical conductivity [S.m-1]": 1e-6,
        "Thermal conductivity [W.m-1.K-1]": 1.8,
        "Specific heat [J.g-1.K-1]": 0.9,
    },
    "Na2Fe2(SO4)3": {
        "Name": "Na2Fe2(SO4)3",
        "Density [g.cm-3]": 3.5,
        "Electrical conductivity [S.m-1]": 1e-7,
        "Thermal conductivity [W.m-1.K-1]": 1.5,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "NaCrO2": {
        "Name": "NaCrO2",
        "Density [g.cm-3]": 4.8,
        "Electrical conductivity [S.m-1]": 1e-4,
        "Thermal conductivity [W.m-1.K-1]": 2.2,
        "Specific heat [J.g-1.K-1]": 0.7,
    },
    "NaMnO2": {
        "Name": "NaMnO2",
        "Density [g.cm-3]": 4.2,
        "Electrical conductivity [S.m-1]": 1e-5,
        "Thermal conductivity [W.m-1.K-1]": 2.0,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "NaNiO2": {
        "Name": "NaNiO2",
        "Density [g.cm-3]": 4.9,
        "Electrical conductivity [S.m-1]": 1e-3,
        "Thermal conductivity [W.m-1.K-1]": 2.5,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "NaCoO2": {
        "Name": "NaCoO2",
        "Density [g.cm-3]": 5.1,
        "Electrical conductivity [S.m-1]": 1e-4,
        "Thermal conductivity [W.m-1.K-1]": 2.8,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "NaTi2(PO4)3": {
        "Name": "NaTi2(PO4)3",
        "Density [g.cm-3]": 2.9,
        "Electrical conductivity [S.m-1]": 1e-8,
        "Thermal conductivity [W.m-1.K-1]": 1.1,
        "Specific heat [J.g-1.K-1]": 0.9,
    },
    "Na2Ti3O7": {
        "Name": "Na2Ti3O7",
        "Density [g.cm-3]": 3.1,
        "Electrical conductivity [S.m-1]": 1e-7,
        "Thermal conductivity [W.m-1.K-1]": 1.3,
        "Specific heat [J.g-1.K-1]": 0.8,
    },
    "Hard Carbon": {
        "Name": "Hard Carbon",
        "Density [g.cm-3]": 1.8,
        "Electrical conductivity [S.m-1]": 1e3,
        "Thermal conductivity [W.m-1.K-1]": 80,
        "Specific heat [J.g-1.K-1]": 0.7,
    },
    "Soft Carbon": {
        "Name": "Soft Carbon",
        "Density [g.cm-3]": 1.6,
        "Electrical conductivity [S.m-1]": 1e4,
        "Thermal conductivity [W.m-1.K-1]": 100,
        "Specific heat [J.g-1.K-1]": 0.7,
    },
    # Lithium metal materials
    "Lithium": {
        "Name": "Lithium",
        "Density [g.cm-3]": 0.534,
        "Electrical conductivity [S.m-1]": 1.1e7,
        "Thermal conductivity [W.m-1.K-1]": 85,
        "Specific heat [J.g-1.K-1]": 3.58,
    },
    "Lithium Metal": {
        "Name": "Lithium Metal",
        "Density [g.cm-3]": 0.534,
        "Electrical conductivity [S.m-1]": 1.1e7,
        "Thermal conductivity [W.m-1.K-1]": 85,
        "Specific heat [J.g-1.K-1]": 3.58,
    },
    # Sodium-ion electrolyte materials
    "NaPF6": {
        "Name": "NaPF6",
        "Density [g.cm-3]": 2.37,
        "Electrical conductivity [S.m-1]": 1e-12,
        "Thermal conductivity [W.m-1.K-1]": 0.2,
        "Specific heat [J.g-1.K-1]": 1.1,
    },
    "NaClO4": {
        "Name": "NaClO4",
        "Density [g.cm-3]": 2.02,
        "Electrical conductivity [S.m-1]": 1e-12,
        "Thermal conductivity [W.m-1.K-1]": 0.2,
        "Specific heat [J.g-1.K-1]": 1.0,
    },
    "NaBF4": {
        "Name": "NaBF4",
        "Density [g.cm-3]": 2.47,
        "Electrical conductivity [S.m-1]": 1e-12,
        "Thermal conductivity [W.m-1.K-1]": 0.2,
        "Specific heat [J.g-1.K-1]": 1.1,
    },
    "NaTFSI": {
        "Name": "NaTFSI",
        "Density [g.cm-3]": 1.96,
        "Electrical conductivity [S.m-1]": 1e-12,
        "Thermal conductivity [W.m-1.K-1]": 0.2,
        "Specific heat [J.g-1.K-1]": 1.2,
    },
    "NaFSI": {
        "Name": "NaFSI",
        "Density [g.cm-3]": 2.15,
        "Electrical conductivity [S.m-1]": 1e-12,
        "Thermal conductivity [W.m-1.K-1]": 0.2,
        "Specific heat [J.g-1.K-1]": 1.1,
    },
    # Add more as needed
}


class Material(BaseModel):
    """
    Material class for representing and managing material properties relevant to battery cell design.

    Class Attributes:
        _aliases (Dict[str, str]): Mapping of internal property names to human-readable aliases with units.

    Args:
        name (str): Name of the material. If the name matches a key in the material database, default properties are loaded.
        density_g_cm3 (float): Density in grams per cubic centimeter.
        electrical_conductivity_S_m (float): Electrical conductivity in Siemens per meter.
        thermal_conductivity_W_mK (float): Thermal conductivity in Watts per meter-Kelvin.
        specific_heat_J_gK (float): Specific heat in Joules per gram-Kelvin.

    Methods:
        as_dict(): Returns a dictionary of the material's properties using internal attribute names.
        as_alias_dict(): Returns a dictionary of the material's properties using human-readable aliases with units.
        from_material(material): Class method to create a Material instance from a name or dict.
        __getitem__(key): Allows dictionary-like access to properties by attribute name or alias.
        __repr__(): Returns a string representation of the Material instance using the alias dictionary.

    Raises:
        KeyError: If a requested property key is not found in the attributes or aliases.
        ValueError: If an unknown material name is provided.
        TypeError: If an invalid type is provided to from_material.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    name: str = Field(..., alias="Name")
    density_g_cm3: float = Field(..., alias="Density [g.cm-3]")
    electrical_conductivity_S_m: float = Field(
        ..., alias="Electrical conductivity [S.m-1]"
    )
    thermal_conductivity_W_mK: float = Field(
        ..., alias="Thermal conductivity [W.m-1.K-1]"
    )
    specific_heat_J_gK: float = Field(..., alias="Specific heat [J.g-1.K-1]")
    
    # Mapping of internal property names to human-readable aliases with units
    _aliases = {
        "name": "Name",
        "density_g_cm3": "Density [g.cm-3]",
        "electrical_conductivity_S_m": "Electrical conductivity [S.m-1]",
        "thermal_conductivity_W_mK": "Thermal conductivity [W.m-1.K-1]",
        "specific_heat_J_gK": "Specific heat [J.g-1.K-1]"
    }

    def __init__(self, *args, **kwargs):
        # String init
        if len(args) == 1 and isinstance(args[0], str) and not kwargs:
            material = args[0]
            if material not in KNOWN_MATERIALS:
                raise ValueError(
                    f"Unknown material: {material}. Allowed materials are: {list(KNOWN_MATERIALS.keys())}"
                )
            kwargs = KNOWN_MATERIALS[material].copy()
            super().__init__(**kwargs)
        # Dict init with "Name"
        elif len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            d = args[0]
            if "Name" in d and d["Name"] in KNOWN_MATERIALS:
                base = KNOWN_MATERIALS[d["Name"]].copy()
                base.update(d)
                super().__init__(**base)
            else:
                super().__init__(**d)
        # Keyword init with Name
        elif "Name" in kwargs and kwargs["Name"] in KNOWN_MATERIALS:
            base = KNOWN_MATERIALS[kwargs["Name"]].copy()
            base.update(kwargs)
            super().__init__(**base)
        else:
            super().__init__(*args, **kwargs)

    @classmethod
    def from_material(cls, material: Union[str, dict]) -> "Material":
        if isinstance(material, Material):
            return material
        if isinstance(material, str):
            if material not in KNOWN_MATERIALS:
                raise ValueError(f"Unknown material: {material}")
            return cls(**KNOWN_MATERIALS[material])
        elif isinstance(material, dict):
            # If only "Name" is provided, use the known material properties
            if "Name" in material and len(material) == 1:
                if material["Name"] not in KNOWN_MATERIALS:
                    raise ValueError(f"Unknown material: {material['Name']}")
                base = KNOWN_MATERIALS[material["Name"]].copy()
                base.update(material)
                return cls(**base)
            else:
                return cls(**material)
        else:
            raise TypeError("Material must be a string or dict")

    def as_dict(self) -> Dict[str, Union[str, float]]:
        return {
            "name": self.name,
            "density_g_cm3": self.density_g_cm3,
            "electrical_conductivity_S_m": self.electrical_conductivity_S_m,
            "thermal_conductivity_W_mK": self.thermal_conductivity_W_mK,
            "specific_heat_J_gK": self.specific_heat_J_gK,
        }

    def as_alias_dict(self) -> Dict[str, float]:
        return {
            "Name": self.name,
            "Density [g.cm-3]": self.density_g_cm3,
            "Electrical conductivity [S.m-1]": self.electrical_conductivity_S_m,
            "Thermal conductivity [W.m-1.K-1]": self.thermal_conductivity_W_mK,
            "Specific heat [J.g-1.K-1]": self.specific_heat_J_gK,
        }

    def __getitem__(self, key: str):
        if key in self._aliases:
            return getattr(self, key)
        for attr, alias in self._aliases.items():
            if key == alias:
                return getattr(self, attr)
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in Material attributes or aliases.")

    def __repr__(self):
        return f"Material({self.as_alias_dict()})"


class MaterialModel(BaseModel):
    name: str = Field(..., description="Material name")
    density_g_cm3: Optional[float] = Field(
        None, alias="Density [g/cm^3]", description="Density in g/cm^3"
    )
    electrical_conductivity_S_m: Optional[float] = Field(
        None,
        alias="Electrical conductivity [S/m]",
        description="Electrical conductivity in S/m",
    )
    thermal_conductivity_W_mK: Optional[float] = Field(
        None,
        alias="Thermal conductivity [W/m.K]",
        description="Thermal conductivity in W/m.K",
    )
    specific_heat_J_gK: Optional[float] = Field(
        None, alias="Specific heat [J/g.K]", description="Specific heat in J/g.K"
    )

    # class Config:
    #     validate_by_name = True
    #     extra = "forbid"
