from typing import Union, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from mcp_server.cell_designer.materials import KNOWN_MATERIALS, find_material_by_alias

def resolve_material_name(material_name: str) -> str:
    """
    Resolve a material name using the alias system.
    
    Args:
        material_name (str): Material name or alias to resolve
        
    Returns:
        str: Canonical material name
        
    Raises:
        ValueError: If material cannot be resolved
    """
    if material_name in KNOWN_MATERIALS:
        return material_name
    
    # Try to resolve using alias system
    resolved = find_material_by_alias(material_name)
    if resolved:
        return resolved
    
    # If still not found, raise error with available materials
    available_materials = list(KNOWN_MATERIALS.keys())
    raise ValueError(
        f"Material '{material_name}' not found in material database. Available materials: {available_materials}"
    )

# Known material database
KNOWN_FORMULATIONS: dict = {
    "NMC811": {
        "Primary active material": "NMC811",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 200,
        "Electrode nominal voltage [V]": 3.77,
    },
    "LFP": {
        "Primary active material": "LFP",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.94,
        "Primary binder mass fraction": 0.03,
        "Primary conductive agent mass fraction": 0.03,
        "Electrode specific capacity [mAh.g-1]": 160,
        "Electrode nominal voltage [V]": 3.4,
    },
    "NMC622": {
        "Primary active material": "NMC622",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 180,
        "Electrode nominal voltage [V]": 3.6,
    },
    "NMC523": {
        "Primary active material": "NMC523",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 160,
        "Electrode nominal voltage [V]": 3.5,
    },
    "NMC111": {
        "Primary active material": "NMC111",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 180,
        "Electrode nominal voltage [V]": 3.7,
    },
    "LCO": {
        "Primary active material": "LCO",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 150,
        "Electrode nominal voltage [V]": 3.9,
    },
    "LNO": {
        "Primary active material": "LNO",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 180,
        "Electrode nominal voltage [V]": 3.8,
    },
    "NCA": {
        "Primary active material": "NCA",
        "Primary binder": "PVDF",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 200,
        "Electrode nominal voltage [V]": 3.67,
    },
    "LTO": {
        "Primary active material": "LTO",
        "Primary binder": "CMC",
        "Primary conductive agent": "Carbon",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Primary conductive agent mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 175,
        "Electrode nominal voltage [V]": 1.55,
    },
    "Graphite": {
        "Primary active material": "Graphite",
        "Primary binder": "CMC",
        "Secondary binder": "SBR",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Secondary binder mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 355,
        "Electrode nominal voltage [V]": 0.1,
    },
    "Si": {
        "Primary active material": "Si",
        "Primary binder": "CMC",
        "Secondary binder": "SBR",
        "Primary active material mass fraction": 0.98,
        "Primary binder mass fraction": 0.01,
        "Secondary binder mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 2863,
        "Electrode nominal voltage [V]": 0.4,
    },
    # Formulations with Si and Graphite
    "Si5%+Graphite95%": {
        "Primary active material": "Graphite",
        "Secondary active material": "Si",
        "Secondary to primary active material mass ratio": "5:95",
        "Primary binder": "CMC",
        "Secondary binder": "SBR",
        "Primary active material mass fraction": 0.98 * 0.95,
        "Secondary active material mass fraction": 0.98 * 0.05,
        "Primary binder mass fraction": 0.01,
        "Secondary binder mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 355 * 0.95 + 2863 * 0.05,
        "Electrode nominal voltage [V]": 0.1 * 0.95 + 0.4 * 0.05,
    },
    "Si10%+Graphite90%": {
        "Primary active material": "Graphite",
        "Secondary active material": "Si",
        "Secondary to primary active material mass ratio": "10:90",
        "Primary binder": "CMC",
        "Secondary binder": "SBR",
        "Primary active material mass fraction": 0.98 * 0.9,
        "Secondary active material mass fraction": 0.98 * 0.1,
        "Primary binder mass fraction": 0.01,
        "Secondary binder mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 355 * 0.9 + 2863 * 0.1,
        "Electrode nominal voltage [V]": 0.1 * 0.9 + 0.4 * 0.1,
    },
    "Si20%+Graphite80%": {
        "Primary active material": "Graphite",
        "Secondary active material": "Si",
        "Secondary to primary active material mass ratio": "20:80",
        "Primary binder": "CMC",
        "Secondary binder": "SBR",
        "Primary active material mass fraction": 0.98 * 0.8,
        "Secondary active material mass fraction": 0.98 * 0.2,
        "Primary binder mass fraction": 0.01,
        "Secondary binder mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 355 * 0.8 + 2863 * 0.2,
        "Electrode nominal voltage [V]": 0.1 * 0.8 + 0.4 * 0.2,
    },
    "Si40%+Graphite60%": {
        "Primary active material": "Graphite",
        "Secondary active material": "Si",
        "Secondary to primary active material mass ratio": "40:60",
        "Primary binder": "CMC",
        "Secondary binder": "SBR",
        "Primary active material mass fraction": 0.98 * 0.6,
        "Secondary active material mass fraction": 0.98 * 0.4,
        "Primary binder mass fraction": 0.01,
        "Secondary binder mass fraction": 0.01,
        "Electrode specific capacity [mAh.g-1]": 355 * 0.6 + 2863 * 0.4,
        "Electrode nominal voltage [V]": 0.1 * 0.6 + 0.4 * 0.4,
    },
}


class ElectrodeFormulation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = Field(..., alias="Name")
    primary_active_material: str = Field(..., alias="Primary active material")
    secondary_active_material: Optional[str] = Field(
        None, alias="Secondary active material"
    )
    secondary_to_primary_active_material_mass_ratio: Optional[str] = Field(
        None, alias="Secondary to primary active material mass ratio"
    )
    primary_binder: str = Field(..., alias="Primary binder")
    secondary_binder: Optional[str] = Field(None, alias="Secondary binder")
    primary_conductive_agent: Optional[str] = Field(
        None, alias="Primary conductive agent"
    )
    secondary_conductive_agent: Optional[str] = Field(
        None, alias="Secondary conductive agent"
    )
    primary_active_material_mass_fraction: float = Field(
        ..., alias="Primary active material mass fraction"
    )
    secondary_active_material_mass_fraction: Optional[float] = Field(
        None, alias="Secondary active material mass fraction"
    )
    primary_binder_mass_fraction: float = Field(
        ..., alias="Primary binder mass fraction"
    )
    secondary_binder_mass_fraction: Optional[float] = Field(
        None, alias="Secondary binder mass fraction"
    )
    primary_conductive_agent_mass_fraction: Optional[float] = Field(
        None, alias="Primary conductive agent mass fraction"
    )
    secondary_conductive_agent_mass_fraction: Optional[float] = Field(
        None, alias="Secondary conductive agent mass fraction"
    )
    electrode_specific_capacity: Optional[float] = Field(
        None, alias="Electrode specific capacity [mAh.g-1]"
    )
    electrode_formulation_density: Optional[float] = Field(
        None, alias="Electrode formulation density [g.cm-3]"
    )
    electrode_nominal_voltage: Optional[float] = Field(
        None, alias="Electrode nominal voltage [V]"
    )

    def __init__(self, *args, **kwargs):
        # String init - only allow known formulations
        if len(args) == 1 and isinstance(args[0], str) and not kwargs:
            material = args[0]
            if material in KNOWN_FORMULATIONS:
                # Use known formulation
                kwargs = KNOWN_FORMULATIONS[material].copy()
                kwargs["Name"] = material  # Ensure Name is set
                super().__init__(**kwargs)
            else:
                # Reject unknown formulations with helpful categorized list and suggestions
                cathode_materials = [
                    "NMC811",
                    "NMC622",
                    "NMC523",
                    "NMC111",
                    "LFP",
                    "LCO",
                    "LNO",
                    "NCA",
                ]
                anode_materials = [
                    "Graphite",
                    "Si",
                    "LTO",
                    "Si5%+Graphite95%",
                    "Si10%+Graphite90%",
                    "Si20%+Graphite80%",
                    "Si40%+Graphite60%",
                ]
                all_materials = cathode_materials + anode_materials

                # Find similar materials (simple string matching)
                suggestions = []
                material_lower = material.lower()
                for mat in all_materials:
                    if material_lower in mat.lower() or mat.lower() in material_lower:
                        suggestions.append(mat)

                error_msg = f"Unknown formulation '{material}'."
                if suggestions:
                    error_msg += f"\n\nDid you mean: {', '.join(suggestions)}?"

                error_msg += "\n\nAvailable formulations:\n"
                error_msg += "Cathode materials: " + ", ".join(cathode_materials) + "\n"
                error_msg += "Anode materials: " + ", ".join(anode_materials)

                raise ValueError(error_msg)
        # Dict init with Name field handling
        elif len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            d = args[0].copy()
            if "Name" in d and d["Name"] in KNOWN_FORMULATIONS:
                # Merge with known formulation data
                base = KNOWN_FORMULATIONS[d["Name"]].copy()
                base.update(d)
                base["Name"] = d["Name"]  # Ensure Name is preserved
                super().__init__(**base)
            else:
                # New formulation from dict - check for mass fraction distribution
                d = self._distribute_mass_fractions(d)
                super().__init__(**d)
        # Keyword init with Name handling
        elif "Name" in kwargs and kwargs["Name"] in KNOWN_FORMULATIONS:
            base = KNOWN_FORMULATIONS[kwargs["Name"]].copy()
            base.update(kwargs)
            super().__init__(**base)
        else:
            # Check for mass fraction distribution in kwargs
            kwargs = self._distribute_mass_fractions(kwargs)
            super().__init__(*args, **kwargs)

    @classmethod
    def _distribute_mass_fractions(cls, data: dict) -> dict:
        """Distribute mass fractions when only active material mass fraction is provided."""
        if not isinstance(data, dict):
            return data

        # Check if only active material mass fraction is provided
        active_material_fraction = data.get("Primary active material mass fraction")
        if active_material_fraction is None:
            return data

        # Check if other mass fractions are already provided
        has_binder_fraction = data.get("Primary binder mass fraction") is not None
        has_conductive_fraction = (
            data.get("Primary conductive agent mass fraction") is not None
        )
        has_secondary_binder_fraction = (
            data.get("Secondary binder mass fraction") is not None
        )

        # If other mass fractions are already provided, don't modify
        if (
            has_binder_fraction
            or has_conductive_fraction
            or has_secondary_binder_fraction
        ):
            return data

        # Calculate remaining mass fraction
        remaining_fraction = 1.0 - active_material_fraction
        if remaining_fraction <= 0:
            return data

        # Determine electrode type based on primary active material
        primary_material = data.get("Primary active material", "")

        # Define cathode and anode materials
        cathode_materials = [
            "NMC811",
            "NMC622",
            "NMC523",
            "NMC111",
            "LFP",
            "LCO",
            "LNO",
            "NCA",
        ]
        anode_materials = ["Graphite", "Si", "LTO"]

        # Check if it's a cathode (positive electrode) or anode (negative electrode)
        is_cathode = any(material in primary_material for material in cathode_materials)
        is_anode = any(material in primary_material for material in anode_materials)

        # Make a copy to avoid modifying the original
        result = data.copy()

        if is_cathode:
            # For positive electrodes: distribute equally between primary binder (PVDF) and conductive agent (Carbon)
            if "Primary binder" not in result:
                result["Primary binder"] = "PVDF"
            if "Primary conductive agent" not in result:
                result["Primary conductive agent"] = "Carbon"

            # Distribute remaining fraction equally
            half_remaining = remaining_fraction / 2
            result["Primary binder mass fraction"] = half_remaining
            result["Primary conductive agent mass fraction"] = half_remaining
        elif is_anode:
            # For negative electrodes: distribute equally between CMC (primary binder) and SBR (secondary binder)
            if "Primary binder" not in result:
                result["Primary binder"] = "CMC"
            if "Secondary binder" not in result:
                result["Secondary binder"] = "SBR"

            # Distribute remaining fraction equally between CMC and SBR
            half_remaining = remaining_fraction / 2
            result["Primary binder mass fraction"] = half_remaining
            result["Secondary binder mass fraction"] = half_remaining
        else:
            # For unknown materials, default to positive electrode behavior
            if "Primary binder" not in result:
                result["Primary binder"] = "PVDF"
            if "Primary conductive agent" not in result:
                result["Primary conductive agent"] = "Carbon"

            # Distribute remaining fraction equally
            half_remaining = remaining_fraction / 2
            result["Primary binder mass fraction"] = half_remaining
            result["Primary conductive agent mass fraction"] = half_remaining

        return result

    @classmethod
    def from_material(cls, material: Union[str, dict]) -> "ElectrodeFormulation":
        if isinstance(material, ElectrodeFormulation):
            return material
        if isinstance(material, str):
            # Use the updated __init__ logic for string materials
            return cls(material)
        elif isinstance(material, dict):
            # Use the updated __init__ logic for dict materials
            return cls(material)
        else:
            raise TypeError("Material must be a string or dict")

    @classmethod
    def get_available_formulations(cls) -> dict:
        """Get categorized list of available electrode formulations"""
        cathode_materials = [
            "NMC811",
            "NMC622",
            "NMC523",
            "NMC111",
            "LFP",
            "LCO",
            "LNO",
            "NCA",
        ]
        anode_materials = [
            "Graphite",
            "Si",
            "LTO",
            "Si5%+Graphite95%",
            "Si10%+Graphite90%",
            "Si20%+Graphite80%",
            "Si40%+Graphite60%",
        ]

        return {
            "cathode": cathode_materials,
            "anode": anode_materials,
            "all": list(KNOWN_FORMULATIONS.keys()),
        }

    def as_alias_dict(self) -> dict:
        return {
            "Name": self.name,
            "Primary active material": self.primary_active_material,
            "Secondary active material": self.secondary_active_material,
            "Secondary to primary active material mass ratio": self.secondary_to_primary_active_material_mass_ratio,
            "Primary binder": self.primary_binder,
            "Secondary binder": self.secondary_binder,
            "Primary conductive agent": self.primary_conductive_agent,
            "Secondary conductive agent": self.secondary_conductive_agent,
            "Primary active material mass fraction": self.primary_active_material_mass_fraction,
            "Secondary active material mass fraction": self.secondary_active_material_mass_fraction,
            "Primary binder mass fraction": self.primary_binder_mass_fraction,
            "Secondary binder mass fraction": self.secondary_binder_mass_fraction,
            "Primary conductive agent mass fraction": self.primary_conductive_agent_mass_fraction,
            "Secondary conductive agent mass fraction": self.secondary_conductive_agent_mass_fraction,
            "Electrode specific capacity [mAh.g-1]": self.electrode_specific_capacity,
            "Electrode formulation density [g.cm-3]": self.electrode_formulation_density,
            "Electrode nominal voltage [V]": self.electrode_nominal_voltage,
        }

    def as_dict(self) -> dict:
        return {
            "Name": self.name,
            "Primary_active_material": self.primary_active_material,
            "Secondary_active_material": self.secondary_active_material,
            "Secondary_to_primary_active_material_mass_ratio": self.secondary_to_primary_active_material_mass_ratio,
            "Primary_binder": self.primary_binder,
            "Secondary_binder": self.secondary_binder,
            "Primary_conductive_agent": self.primary_conductive_agent,
            "Secondary_conductive_agent": self.secondary_conductive_agent,
            "Primary_active_material_mass_fraction": self.primary_active_material_mass_fraction,
            "Secondary_active_material_mass_fraction": self.secondary_active_material_mass_fraction,
            "Primary_binder_mass_fraction": self.primary_binder_mass_fraction,
            "Secondary_binder_mass_fraction": self.secondary_binder_mass_fraction,
            "Primary_conductive_agent_mass_fraction": self.primary_conductive_agent_mass_fraction,
            "Secondary_conductive_agent_mass_fraction": self.secondary_conductive_agent_mass_fraction,
            "Electrode_specific_capacity": self.electrode_specific_capacity,
            "Electrode_formulation_density": self.electrode_formulation_density,
            "Electrode_nominal_voltage": self.electrode_nominal_voltage,
        }

    # Calculate formulation density - moved to model validator for immediate availability
    def _calculate_electrode_formulation_density(self) -> float:
        # Calculate the density based on mass fractions and known material densities
        total_mass = (
            self.primary_active_material_mass_fraction
            + (self.secondary_active_material_mass_fraction or 0)
            + self.primary_binder_mass_fraction
            + (self.secondary_binder_mass_fraction or 0)
            + (self.primary_conductive_agent_mass_fraction or 0)
            + (self.secondary_conductive_agent_mass_fraction or 0)
        )
        if self.primary_active_material in KNOWN_MATERIALS:
            primary_active_material_density = KNOWN_MATERIALS[
                self.primary_active_material
            ]["Density [g.cm-3]"]
        else:
            # Try to resolve using alias system
            resolved_primary = resolve_material_name(self.primary_active_material)
            primary_active_material_density = KNOWN_MATERIALS[resolved_primary][
                "Density [g.cm-3]"
            ]
        if self.secondary_active_material is not None:
            if self.secondary_active_material in KNOWN_MATERIALS:
                secondary_active_material_density = KNOWN_MATERIALS[
                    self.secondary_active_material
                ]["Density [g.cm-3]"]
            else:
                # Try to resolve using alias system
                resolved_secondary = resolve_material_name(self.secondary_active_material)
                secondary_active_material_density = KNOWN_MATERIALS[resolved_secondary][
                    "Density [g.cm-3]"
                ]
        else:
            secondary_active_material_density = 1.0  # Default density if unknown
        if self.primary_binder in KNOWN_MATERIALS:
            primary_binder_density = KNOWN_MATERIALS[self.primary_binder][
                "Density [g.cm-3]"
            ]
        else:
            raise ValueError(
                f"Primary binder '{self.primary_binder}' not found in material database. Available materials: {list(KNOWN_MATERIALS.keys())}"
            )
        if self.secondary_binder is not None:
            if self.secondary_binder in KNOWN_MATERIALS:
                secondary_binder_density = KNOWN_MATERIALS[self.secondary_binder][
                    "Density [g.cm-3]"
                ]
            else:
                raise ValueError(
                    f"Secondary binder '{self.secondary_binder}' not found in material database. Available materials: {list(KNOWN_MATERIALS.keys())}"
                )
        else:
            secondary_binder_density = 1.0  # Default density if unknown
        if self.primary_conductive_agent is not None:
            if self.primary_conductive_agent in KNOWN_MATERIALS:
                primary_conductive_agent_density = KNOWN_MATERIALS[
                    self.primary_conductive_agent
                ]["Density [g.cm-3]"]
            else:
                raise ValueError(
                    f"Primary conductive agent '{self.primary_conductive_agent}' not found in material database. Available materials: {list(KNOWN_MATERIALS.keys())}"
                )
        else:
            primary_conductive_agent_density = 1.0
        if self.secondary_conductive_agent is not None:
            if self.secondary_conductive_agent in KNOWN_MATERIALS:
                secondary_conductive_agent_density = KNOWN_MATERIALS[
                    self.secondary_conductive_agent
                ]["Density [g.cm-3]"]
            else:
                raise ValueError(
                    f"Secondary conductive agent '{self.secondary_conductive_agent}' not found in material database. Available materials: {list(KNOWN_MATERIALS.keys())}"
                )
        else:
            secondary_conductive_agent_density = 1.0  # Default density if unknown

        total_volume = (
            self.primary_active_material_mass_fraction / primary_active_material_density
            + (self.secondary_active_material_mass_fraction or 0)
            / secondary_active_material_density
            + self.primary_binder_mass_fraction / primary_binder_density
            + (self.secondary_binder_mass_fraction or 0) / secondary_binder_density
            + (self.primary_conductive_agent_mass_fraction or 0)
            / primary_conductive_agent_density
            + (self.secondary_conductive_agent_mass_fraction or 0)
            / secondary_conductive_agent_density
        )
        if total_volume == 0:
            raise ValueError(
                "Total electrode volume cannot be zero for density calculation"
            )
        # Calculate the density using the formula: density = mass/volume
        # Here, we assume a simple model where volume is proportional to mass
        formulation_density = total_mass / total_volume
        if formulation_density <= 1.5:
            raise ValueError(
                "Electrode formulation density must be greater than 1.5 g.cm-3"
            )
        return round(formulation_density, 3)  # Normalize by total mass

    @model_validator(mode="after")
    def validate_blend_and_fractions(self):
        # Blend logic
        # Blend logic: check if this is a blend based on primary/secondary active materials and their mass fractions
        if (
            self.primary_active_material
            and self.secondary_active_material
            and self.secondary_active_material_mass_fraction is not None
        ):
            # Validate that primary and secondary are not the same
            if self.primary_active_material == self.secondary_active_material:
                raise ValueError(
                    "Primary and secondary active materials cannot be the same in a blend"
                )
            if not self.secondary_to_primary_active_material_mass_ratio:
                raise ValueError(
                    "Blend materials must specify the secondary to primary active material mass ratio"
                )
            # Check ratio
            try:
                ratio_parts = (
                    self.secondary_to_primary_active_material_mass_ratio.split(":")
                )
                if len(ratio_parts) == 2:
                    secondary_ratio = float(ratio_parts[0])
                    primary_ratio = float(ratio_parts[1])
                    expected_ratio = (
                        primary_ratio / secondary_ratio
                        if secondary_ratio != 0
                        else None
                    )
                    actual_ratio = (
                        self.primary_active_material_mass_fraction
                        / self.secondary_active_material_mass_fraction
                        if self.secondary_active_material_mass_fraction != 0
                        else None
                    )
                    if (
                        expected_ratio is not None
                        and actual_ratio is not None
                        and round(actual_ratio, 2) != round(expected_ratio, 2)
                    ):
                        raise ValueError(
                            "Primary and secondary active material mass fractions do not match the specified ratio"
                        )
            except Exception:
                raise ValueError(
                    "Invalid format for secondary to primary active material mass ratio"
                )
            # Parse the blend composition from the object representation, not from a 'name' attribute
            parts = []
            if (
                self.primary_active_material
                and self.primary_active_material_mass_fraction is not None
            ):
                parts.append(
                    f"{self.primary_active_material}{int(round(self.primary_active_material_mass_fraction * 100))}%"
                )
            if (
                self.secondary_active_material
                and self.secondary_active_material_mass_fraction is not None
            ):
                parts.append(
                    f"{self.secondary_active_material}{int(round(self.secondary_active_material_mass_fraction * 100))}%"
                )
            if len(parts) != 2:
                raise ValueError(
                    "Blend material must have both primary and secondary active materials with their mass fractions"
                )
            # The one with the higher mass fraction is primary
            first_name, first_frac = (
                self.primary_active_material,
                self.primary_active_material_mass_fraction,
            )
            second_name, second_frac = (
                self.secondary_active_material,
                self.secondary_active_material_mass_fraction,
            )
            primary = (first_name, first_frac)
            secondary = (second_name, second_frac)
            if primary[1] < secondary[1]:
                primary, secondary = secondary, primary
            self.primary_active_material = primary[0]
            self.secondary_active_material = secondary[0]
            self.secondary_to_primary_active_material_mass_ratio = (
                f"{secondary[1]}:{primary[1]}"
            )
            self.primary_active_material_mass_fraction = primary[1]
            self.secondary_active_material_mass_fraction = secondary[1]
            if primary[0] == secondary[0]:
                raise ValueError(
                    "Primary and secondary active materials cannot be the same in a blend"
                )
            if not self.primary_active_material or not self.secondary_active_material:
                raise ValueError(
                    "Blend materials must specify both primary and secondary active materials"
                )
            if not self.secondary_to_primary_active_material_mass_ratio:
                raise ValueError(
                    "Blend materials must specify the secondary to primary active material mass ratio"
                )
            # Check ratio
            ps_ratio = float(primary[1]) / float(secondary[1])
            if (
                self.secondary_active_material_mass_fraction
                and self.primary_active_material_mass_fraction
            ):
                if round(
                    self.primary_active_material_mass_fraction
                    / self.secondary_active_material_mass_fraction,
                    1,
                ) != round(ps_ratio, 1):
                    raise ValueError(
                        "Primary and secondary active material mass fractions do not match the specified ratio"
                    )
        # Validate mass fractions
        if not (0 < self.primary_active_material_mass_fraction <= 1):
            raise ValueError("Primary active material mass fraction must be in (0, 1]")
        if self.secondary_active_material_mass_fraction is not None:
            if not (0 <= self.secondary_active_material_mass_fraction <= 1):
                raise ValueError(
                    "Secondary active material mass fraction must be in [0, 1]"
                )
        # Validate that all mass fractions sum to approximately 1
        components = [
            ("primary active material", self.primary_active_material_mass_fraction),
            (
                "secondary active material",
                self.secondary_active_material_mass_fraction or 0,
            ),
            ("primary binder", self.primary_binder_mass_fraction),
            ("secondary binder", self.secondary_binder_mass_fraction or 0),
            (
                "primary conductive agent",
                self.primary_conductive_agent_mass_fraction or 0,
            ),
            (
                "secondary conductive agent",
                self.secondary_conductive_agent_mass_fraction or 0,
            ),
        ]

        total = sum(fraction for _, fraction in components)

        if abs(total - 1.0) > 1e-6:  # Allow for floating point precision errors
            self._distribute_mass_fractions(self.as_dict())
            # Validate that all mass fractions sum to approximately 1
            components = [
                ("primary active material", self.primary_active_material_mass_fraction),
                (
                    "secondary active material",
                    self.secondary_active_material_mass_fraction or 0,
                ),
                ("primary binder", self.primary_binder_mass_fraction),
                ("secondary binder", self.secondary_binder_mass_fraction or 0),
                (
                    "primary conductive agent",
                    self.primary_conductive_agent_mass_fraction or 0,
                ),
                (
                    "secondary conductive agent",
                    self.secondary_conductive_agent_mass_fraction or 0,
                ),
            ]
            total = sum(fraction for _, fraction in components)
            # Provide detailed breakdown for better debugging
            breakdown = ", ".join(
                [
                    f"{name}: {fraction:.6f}"
                    for name, fraction in components
                    if fraction > 0
                ]
            )
            #Redistribute the mass fractions
            if abs(total - 1.0) > 1e-6:
                raise ValueError(
                    f"Mass fractions must sum to exactly 1.0, but got {total:.6f}. "
                    f"Breakdown: {breakdown}"
                )
        # Check if specific capacity and nominal voltage are provided
        if self.electrode_specific_capacity is None:
            # If not provided, calculate from known materials
            if self.primary_active_material in KNOWN_MATERIALS:
                self.electrode_specific_capacity = KNOWN_MATERIALS[
                    self.primary_active_material
                ]["Electrode specific capacity [mAh.g-1]"]
            else:
                raise ValueError(
                    f"Specific capacity not provided and unknown for primary active material: {self.primary_active_material}"
                )
        if self.electrode_nominal_voltage is None:
            # If not provided, calculate from known materials
            if self.primary_active_material in KNOWN_MATERIALS:
                self.electrode_nominal_voltage = KNOWN_MATERIALS[
                    self.primary_active_material
                ]["Electrode nominal voltage [V]"]
            else:
                raise ValueError(
                    f"Nominal voltage not provided and unknown for primary active material: {self.primary_active_material}"
                )

        # Calculate electrode formulation density if not provided
        if self.electrode_formulation_density is None:
            self.electrode_formulation_density = (
                self._calculate_electrode_formulation_density()
            )

        return self

    @property
    def electrode_formulation_density_g_cm3(self) -> float:
        """Backward compatibility property for computed field access"""
        if self.electrode_formulation_density is None:
            self.electrode_formulation_density = (
                self._calculate_electrode_formulation_density()
            )
        return self.electrode_formulation_density

    def get(self, key, default=None):
        # For compatibility with old code
        return getattr(self, key, default)

    def __getitem__(self, key):
        # For compatibility with old code
        return getattr(self, key)

    def __repr__(self) -> str:
        props = ", ".join(
            f"{k}={getattr(self, k)!r}" for k in self.__class__.model_fields
        )
        return f"ElectrodeFormulation({props})"
