from pydantic import (
    BaseModel,
    Field,
    computed_field,
    field_validator,
    model_validator,
)
from typing import Union
import numpy as np
from .electrode_formulation import ElectrodeFormulation
from .electrolyte_composition import ElectrolyteComposition
from .materials import KNOWN_MATERIALS, Material

# Global constraints
CELL_MIN_VOLUME_PACKING_RATIO = 0.75
CELL_MAX_VOLUME_PACKING_RATIO = 0.99

POSITIVE_ELECTRODE_MASS_LOADING_MIN = 15
POSITIVE_ELECTRODE_MASS_LOADING_MAX = 25
NEGATIVE_ELECTRODE_MASS_LOADING_MIN = 8
NEGATIVE_ELECTRODE_MASS_LOADING_MAX = 18

POSITIVE_ELECTRODE_POROSITY_MIN = 0.15
POSITIVE_ELECTRODE_POROSITY_MAX = 0.37
NEGATIVE_ELECTRODE_POROSITY_MIN = 0.15
NEGATIVE_ELECTRODE_POROSITY_MAX = 0.37

POSITIVE_ELECTRODE_ACTIVE_MATERIAL_VOLUME_FRACTION_MIN = 0
POSITIVE_ELECTRODE_ACTIVE_MATERIAL_VOLUME_FRACTION_MAX = 1
NEGATIVE_ELECTRODE_ACTIVE_MATERIAL_VOLUME_FRACTION_MIN = 0
NEGATIVE_ELECTRODE_ACTIVE_MATERIAL_VOLUME_FRACTION_MAX = 1

POSITIVE_ELECTRODE_COATING_THICKNESS_MIN = 30
POSITIVE_ELECTRODE_COATING_THICKNESS_MAX = 100
NEGATIVE_ELECTRODE_COATING_THICKNESS_MIN = 30
NEGATIVE_ELECTRODE_COATING_THICKNESS_MAX = 120

POSITIVE_ELECTRODE_FOIL_THICKNESS_MIN = 12
POSITIVE_ELECTRODE_FOIL_THICKNESS_MAX = 24
NEGATIVE_ELECTRODE_FOIL_THICKNESS_MIN = 6
NEGATIVE_ELECTRODE_FOIL_THICKNESS_MAX = 12


class CellDesign(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)

    def optimize_electrode_coating_thickness(self, electrode: str):
        """
        Adjust the coating thickness for the given electrode ('positive' or 'negative')
        so that the coating density and porosity are within validation limits, given the current mass loading.
        """
        if electrode not in ["positive", "negative"]:
            raise ValueError(f"Electrode is {electrode} but must be 'positive' or 'negative'")

        # Get current values
        mass_loading = getattr(self, f"{electrode}_electrode_mass_loading_mg_cm2")
        coating_thickness = getattr(self, f"{electrode}_electrode_coating_thickness_um")

        # Get formulation density
        form = self._get_electrode_formulation(electrode)
        formulation_density = form.electrode_formulation_density_g_cm3

        # Validation limits
        coating_density_min, coating_density_max = (
            0.63 * formulation_density,
            0.85 * formulation_density,
        )
        thickness_min, thickness_max = mass_loading * 1e-3 / (
            coating_density_max * 1e-4
        ), mass_loading * 1e-3 / (
            coating_density_min * 1e-4
        )  # Example limits in micrometers

        if not (thickness_min <= coating_thickness <= thickness_max):
            # If current thickness is out of bounds, try to adjust it
            raise ValueError(
                f"{electrode.capitalize()} electrode coating thickness {coating_thickness} um is out of bounds "
                f"({thickness_min} - {thickness_max} um) for mass loading {mass_loading} mg/cm² and formulation density {formulation_density} g/cm³."
            )
        # Optionally, you could return the chosen thickness
        return getattr(self, f"{electrode}_electrode_coating_thickness_um")

    """
    Battery cell design model with input parameters and computed properties.

    Supports prismatic, cylindrical, and pouch form factors with validation.
    Key parameters: electrodes, separator, electrolyte, casing, and dimensions.
    """

    form_factor: str = Field("Prismatic", alias="Form factor")
    cell_height_mm: float = Field(100, alias="Cell height [mm]")
    cell_volume_packing_ratio: float = Field(0.9, alias="Cell volume packing ratio")
    cell_casing_thickness_mm: float = Field(0.8, alias="Cell casing thickness [mm]")
    cell_casing_material: dict = Field(
        Material(Name="Aluminum").as_alias_dict(), alias="Cell casing material"
    )
    cell_thermal_resistance_K_W: float = Field(
        0.15, alias="Cell thermal resistance [K.W-1]"
    )
    cell_electrode_overhang_mm: float = Field(0.5, alias="Cell electrode overhang [mm]")
    upper_voltage_cutoff_V: float = Field(4.2, alias="Upper voltage cut-off [V]")
    lower_voltage_cutoff_V: float = Field(2.8, alias="Lower voltage cut-off [V]")
    jelly_roll_count: int = Field(1, alias="Jelly roll count")

    # Electrode properties
    positive_electrode_formulation: dict = Field(
        ElectrodeFormulation(Name="NMC811").as_alias_dict(),
        alias="Positive electrode formulation",
    )
    positive_electrode_sheet_count: int = Field(
        80, alias="Positive electrode sheet count"
    )
    positive_electrode_mass_loading_mg_cm2: float = Field(
        15, alias="Positive electrode mass loading [mg.cm-2]"
    )
    positive_electrode_coating_thickness_um: float = Field(
        50, alias="Positive electrode coating thickness [um]"
    )
    positive_electrode_foil_thickness_um: float = Field(
        12, alias="Positive electrode foil thickness [um]"
    )
    positive_electrode_foil_density_g_cm3: float = Field(
        2.7, alias="Positive electrode foil density [g.cm-3]"
    )
    negative_electrode_formulation: dict = Field(
        ElectrodeFormulation("Graphite").as_alias_dict(),
        alias="Negative electrode formulation",
    )
    negative_electrode_mass_loading_mg_cm2: float = Field(
        10, alias="Negative electrode mass loading [mg.cm-2]"
    )
    negative_electrode_coating_thickness_um: float = Field(
        60, alias="Negative electrode coating thickness [um]"
    )
    negative_electrode_foil_thickness_um: float = Field(
        6, alias="Negative electrode foil thickness [um]"
    )
    negative_electrode_foil_density_g_cm3: float = Field(
        8.96, alias="Negative electrode foil density [g.cm-3]"
    )
    negative_current_collector_thickness_m: float = Field(
        0.000016, alias="Negative current collector thickness [m]"
    )
    separator_composition: str = Field(
        "Ceramic coated PE", alias="Separator composition"
    )
    separator_thickness_um: float = Field(12, alias="Separator thickness [um]")
    separator_areal_density_g_m2: float = Field(
        12, alias="Separator areal density [g.m-2]"
    )
    separator_porosity: float = Field(0.42, alias="Separator porosity")
    electrolyte_composition: Union[ElectrolyteComposition, dict, str] = Field(
        ElectrolyteComposition(name="EC/DMC/EMC (2:4:4)"),
        alias="Electrolyte composition",
    )

    def _get_electrode_formulation(
        self, electrode_type_or_formulation
    ) -> ElectrodeFormulation:
        """Helper to convert electrode formulation to ElectrodeFormulation object."""
        if isinstance(
            electrode_type_or_formulation, str
        ) and electrode_type_or_formulation in ["positive", "negative"]:
            # If it's a string like "positive" or "negative", get the formulation attribute
            formulation = getattr(
                self, f"{electrode_type_or_formulation}_electrode_formulation"
            )
        else:
            # If it's already a formulation object or dict, use it directly
            formulation = electrode_type_or_formulation

        if isinstance(formulation, ElectrodeFormulation):
            return formulation
        elif isinstance(formulation, dict):
            return ElectrodeFormulation(**formulation)
        elif isinstance(formulation, str):
            return ElectrodeFormulation.from_material(formulation)
        return formulation

    @staticmethod
    def _validate_range(
        value: float, min_val: float, max_val: float, param_name: str, unit: str = ""
    ) -> float:
        """Helper to validate value is within range."""
        MSG = ""
        if not (min_val <= value <= max_val):
            if "loading" in param_name.lower():
                MSG = f"Or consider reducing the active material mass fraction by {min_val/value:.2f}."
            unit_str = f" {unit}" if unit else ""
            raise ValueError(
                f"{param_name} is {value} but must be between {min_val} and {max_val}{unit_str}. {MSG}"
            )
        return value

    # class Config:
    #     validate_by_field_name = True
    #     arbitrary_types_allowed = True

    # --- Computed fields for derived properties ---

    @classmethod
    def _process_materials_and_formulations(cls, overrides: dict) -> dict:
        """Process electrode formulations and cell casing materials in overrides dict"""
        processed_overrides = overrides.copy()

        # Convert electrode formulations
        for key in ["Positive electrode formulation", "Negative electrode formulation"]:
            if key in processed_overrides:
                formulation_data = processed_overrides[key]
                if isinstance(formulation_data, str):
                    ef = ElectrodeFormulation(formulation_data)
                elif isinstance(formulation_data, dict):
                    try:
                        # Apply mass fraction distribution before creating ElectrodeFormulation
                        processed_data = ElectrodeFormulation._distribute_mass_fractions(formulation_data)
                        
                        # Try to create with processed data
                        ef = ElectrodeFormulation(**processed_data)
                    except Exception as e:
                        # If that fails, check if Name is provided to use it for defaults
                        if "Name" in formulation_data:
                            # Use the name to create base formulation then update with provided data
                            ef = ElectrodeFormulation(formulation_data["Name"])
                            ef_dict = ef.as_alias_dict()
                            ef_dict.update(formulation_data)
                            # Apply mass fraction distribution to the merged data
                            processed_dict = ElectrodeFormulation._distribute_mass_fractions(ef_dict)
                            ef = ElectrodeFormulation(**processed_dict)
                        else:
                            # Only use hard defaults if no Name is provided
                            default_material = (
                                "NMC811" if "Positive" in key else "Graphite"
                            )
                            ef = ElectrodeFormulation(default_material)
                            # Update the electrode formulation with provided overrides
                            ef_dict = ef.as_alias_dict()
                            ef_dict.update(formulation_data)
                            # Apply mass fraction distribution to the final data
                            processed_dict = ElectrodeFormulation._distribute_mass_fractions(ef_dict)
                            ef = ElectrodeFormulation(**processed_dict)
                else:
                    continue
                processed_overrides[key] = ef.as_alias_dict()

        # Convert "Cell casing material" to Material object
        if "Cell casing material" in processed_overrides:
            material_data = processed_overrides["Cell casing material"]
            if isinstance(material_data, str):
                material = Material(material_data)
            elif isinstance(material_data, dict):
                material = Material(**material_data)
            else:
                material = None

            if material:
                processed_overrides["Cell casing material"] = material.as_alias_dict()

        return processed_overrides

    @classmethod
    def from_overrides(cls, overrides: dict) -> "CellDesign":
        # Process electrode formulations and materials first
        processed_overrides = cls._process_materials_and_formulations(overrides or {})

        form_factor = processed_overrides.get("Form factor", "Prismatic").lower()
        if form_factor == "cylindrical":
            return CylindricalCellDesignParameters(**processed_overrides)
        elif form_factor == "pouch":
            return PouchCellDesignParameters(**processed_overrides)
        else:
            return PrismaticCellDesignParameters(**processed_overrides)

    @computed_field(alias="Cell nominal voltage [V]")
    def cell_nominal_voltage_V(self) -> float:
        pos = self._get_electrode_formulation("positive")
        neg = self._get_electrode_formulation("negative")
        return round(pos.electrode_nominal_voltage - neg.electrode_nominal_voltage, 3)

    @computed_field(alias="Cell nominal capacity [A.h]")
    def cell_nominal_capacity_Ah(self) -> float:
        pos = self._get_electrode_formulation("positive")
        pos_capacity_Ah_g = pos.electrode_specific_capacity * 1e-3

        return round(
            (
                2
                * self.positive_electrode_sheet_count
                * self.positive_electrode_sheet_height_mm
                * self.positive_electrode_sheet_width_mm
                * 1e-2
                * self.positive_electrode_mass_loading_mg_cm2
                * 1e-3
                * pos_capacity_Ah_g
                * pos.primary_active_material_mass_fraction
            ),
            3,
        )

    @computed_field(alias="Cell nominal energy [W.h]")
    def cell_nominal_energy_Wh(self) -> float:
        return round(self.cell_nominal_voltage_V * self.cell_nominal_capacity_Ah, 3)

    @computed_field(alias="Cell N/P ratio")
    def cell_n_p_ratio(self) -> float:
        pos = self._get_electrode_formulation("positive")
        neg = self._get_electrode_formulation("negative")

        pos_capacity = (
            pos.electrode_specific_capacity
            * self.positive_electrode_mass_loading_mg_cm2
            * pos.primary_active_material_mass_fraction
        )
        neg_capacity = (
            neg.electrode_specific_capacity
            * self.negative_electrode_mass_loading_mg_cm2
            * neg.primary_active_material_mass_fraction
        )

        npr = neg_capacity / pos_capacity
        neg_ml_min = (
            pos_capacity
            / (
                neg.primary_active_material_mass_fraction
                * neg.electrode_specific_capacity
            )
            * 1.0
        )
        neg_ml_max = (
            pos_capacity
            / (
                neg.primary_active_material_mass_fraction
                * neg.electrode_specific_capacity
            )
            * 1.2
        )
        if not (1 <= npr <= 1.2):
            MSG = f"N/P ratio {npr:.2f} must be between 1.0 and 1.2. "
            MSG += f"With the current positive electrode mass loading of {self.positive_electrode_mass_loading_mg_cm2} mg/cm²"
            if neg_ml_min <= NEGATIVE_ELECTRODE_MASS_LOADING_MIN:
                neg_active_material_mass_fraction = neg_ml_min * neg.primary_active_material_mass_fraction/NEGATIVE_ELECTRODE_MASS_LOADING_MIN

                MSG += f" the negative electrode active material mass fraction, which is {neg.primary_active_material_mass_fraction}, should be less than {neg_active_material_mass_fraction:.2f}, and"
                MSG += f" the negative electrode mass loading, which is {self.negative_electrode_mass_loading_mg_cm2}, "
                MSG += f" should be more than {neg_ml_min:.2f} mg/cm²."
                neg_ml_min = NEGATIVE_ELECTRODE_MASS_LOADING_MIN
            else:
                MSG += f" and negative electrode active material mass fraction of {neg.primary_active_material_mass_fraction}, "
                MSG += f" the negative electrode mass loading, which is {self.negative_electrode_mass_loading_mg_cm2}, "
                MSG += f" should be between {neg_ml_min:.2f} and {neg_ml_max:.2f} mg/cm²."
            raise ValueError(
                MSG
            )
        return round(npr, 3)

    @computed_field(alias="Cell current density [A.cm-2]")
    def cell_current_density_A_cm2(self) -> float:
        # Calculate cell current density based on cell dimensions and jelly roll properties
        active_area_cm2 = (
            self.positive_electrode_sheet_height_mm
            * self.positive_electrode_sheet_width_mm
            * self.positive_electrode_sheet_count
            * 2
            * 1e-4
        )
        return round(self.cell_nominal_capacity_Ah / active_area_cm2, 3)

    @computed_field(alias="Cell volume [L]")
    def cell_volume_L(self) -> float:
        if (
            hasattr(self, "cell_height_mm")
            and hasattr(self, "cell_width_mm")
            and hasattr(self, "cell_thickness_mm")
        ):
            volume = (
                self.cell_height_mm * self.cell_width_mm * self.cell_thickness_mm * 1e-6
            )  # mm3 to L
            return round(volume, 3)
        return None

    @computed_field(alias="Cell mass [g]")
    def cell_mass_g(self) -> float:
        # Calculate cell mass based on jelly roll mass and electrolyte mass
        return round(
            self.jelly_roll_mass_g + self.electrolyte_mass_g + self.cell_casing_mass_g,
            3,
        )

    @computed_field(alias="Cell casing mass [g]")
    def cell_casing_mass_g(self) -> float:
        # Convert mm to cm
        return round(100, 3)  # Placeholder for cell casing mass calculation

    # Jelly roll properties
    @computed_field(alias="Jelly roll height [mm]")
    def jelly_roll_height_mm(self) -> float:
        return round(self.cell_height_mm * self.cell_volume_packing_ratio ** (1 / 2), 3)

    @computed_field(alias="Jelly roll mass [g]")
    def jelly_roll_mass_g(self) -> float:
        return round(
            1000, 3
        )  # Placeholder for jelly roll mass calculation, to be implemented based on electrode properties

    @computed_field(alias="Jelly roll volume [L]")
    def jelly_roll_volume_L(self) -> float:
        return (
            round(self.cell_volume_L * self.cell_volume_packing_ratio, 3)
            if self.cell_volume_L
            else None
        )

    # -- Electrode properties --
    # Positive electrode properties
    @computed_field(alias="Positive electrode sheet height [mm]")
    def positive_electrode_sheet_height_mm(self) -> float:
        return round(self.jelly_roll_height_mm - 4 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Positive electrode sheet thickness [mm]")
    def positive_electrode_sheet_thickness_um(self) -> float:
        return round(
            self.positive_electrode_coating_thickness_um * 2
            + self.positive_electrode_foil_thickness_um,
            3,
        )

    @computed_field(alias="Positive electrode sheet width [mm]")
    def positive_electrode_sheet_width_mm(self) -> float:
        return round(
            250, 3
        )  # Placeholder for positive electrode sheet width, to be defined based on design

    @computed_field(alias="Positive electrode coating density [g.cm-3]")
    def positive_electrode_coating_density_g_cm3(self) -> float:
        return round(
            (
                self.positive_electrode_mass_loading_mg_cm2
                * 1e-3
                / (self.positive_electrode_coating_thickness_um * 1e-4)
            ),
            3,
        )

    @computed_field(alias="Positive electrode porosity")
    def positive_electrode_porosity(self) -> float:
        pos = self._get_electrode_formulation("positive")
        porosity = 1 - (
            self.positive_electrode_coating_density_g_cm3
            / pos.electrode_formulation_density_g_cm3
        )
        porosity_min, porosity_max = 0.15, 0.37
        coating_thickness_min = (
            self.positive_electrode_mass_loading_mg_cm2
            * 1e-3
            / ((1 - porosity_min) * pos.electrode_formulation_density_g_cm3 * 1e-4)
        )
        coating_thickness_max = (
            self.positive_electrode_mass_loading_mg_cm2
            * 1e-3
            / ((1 - porosity_max) * pos.electrode_formulation_density_g_cm3 * 1e-4)
        )
        if porosity < porosity_min or porosity > porosity_max:
            MSG = f"Calculated positive electrode porosity {porosity:.3f} is outside the valid range [0.15, 0.37]. "
            MSG += f"Set the positive electrode coating thickness, which is {self.positive_electrode_coating_thickness_um}, between {coating_thickness_min:.3f} um and {coating_thickness_max:.3f} um."
            raise ValueError(MSG)
        return round(porosity, 3)

    @computed_field(alias="Positive electrode active material volume fraction")
    def positive_electrode_active_material_volume_fraction(self) -> float:
        pos_form = self._get_electrode_formulation("positive")
        material_density = KNOWN_MATERIALS[pos_form.primary_active_material][
            "Density [g.cm-3]"
        ]
        return round(
            (
                self.positive_electrode_mass_loading_mg_cm2
                * 1e-3
                * pos_form.primary_active_material_mass_fraction
            )
            / (material_density * self.positive_electrode_coating_thickness_um * 1e-4),
            3,
        )

    # Negative electrode properties
    @computed_field(alias="Negative electrode sheet count")
    def negative_electrode_sheet_count(self) -> int:
        return self.positive_electrode_sheet_count + 1

    @computed_field(alias="Negative electrode sheet width [mm]")
    def negative_electrode_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm + 2 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Negative electrode sheet height [mm]")
    def negative_electrode_sheet_height_mm(self) -> float:
        return round(self.jelly_roll_height_mm - 2 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Negative electrode sheet thickness [um]")
    def negative_electrode_sheet_thickness_um(self) -> float:
        return round(
            self.negative_electrode_coating_thickness_um * 2
            + self.negative_electrode_foil_thickness_um,
            3,
        )

    # @computed_field(alias="Negative electrode mass loading [mg.cm-2]")
    # def negative_electrode_mass_loading_mg_cm2(self) -> float:
    #     return self.negative_electrode_mass_loading_mg_cm2

    @computed_field(alias="Negative electrode coating density [g.cm-3]")
    def negative_electrode_coating_density_g_cm3(self) -> float:
        return round(
            self.negative_electrode_mass_loading_mg_cm2
            * 1e-3
            / (self.negative_electrode_coating_thickness_um * 1e-4),
            3,
        )

    @computed_field(alias="Negative electrode porosity")
    def negative_electrode_porosity(self) -> float:
        # Calculate porosity based on coating density and electrode formulation density
        neg = self._get_electrode_formulation("negative")

        coating_density = self.negative_electrode_coating_density_g_cm3
        formulation_density = neg.electrode_formulation_density_g_cm3

        if formulation_density <= 0:
            raise ValueError(f"Electrode formulation density, which is {formulation_density}, must be greater than zero.")

        porosity = 1 - (coating_density / formulation_density)
        # Validate porosity range
        porosity_min, porosity_max = NEGATIVE_ELECTRODE_POROSITY_MIN, NEGATIVE_ELECTRODE_POROSITY_MAX
        coating_thickness_min = (
            self.negative_electrode_mass_loading_mg_cm2
            * 1e-3
            / ((1 - porosity_min) * formulation_density * 1e-4)
        )
        coating_thickness_max = (
            self.negative_electrode_mass_loading_mg_cm2
            * 1e-3
            / ((1 - porosity_max) * formulation_density * 1e-4)
        )
        if porosity < porosity_min or porosity > porosity_max:
            MSG = f"Calculated negative electrode porosity {porosity:.3f} is outside the valid range [{porosity_min}, {porosity_max}]. "
            MSG += f"Set the negative electrode coating thickness, which is {self.negative_electrode_coating_thickness_um}, between {coating_thickness_min:.3f} um and {coating_thickness_max:.3f} um."
            raise ValueError(MSG)
        return round(porosity, 3)

    @computed_field(alias="Negative electrode active material volume fraction")
    def negative_electrode_active_material_volume_fraction(self) -> float:
        neg_form = self._get_electrode_formulation("negative")
        return round(
            self.negative_electrode_mass_loading_mg_cm2
            * 1e-3
            * neg_form.primary_active_material_mass_fraction
            / (
                KNOWN_MATERIALS[neg_form.primary_active_material]["Density [g.cm-3]"]
                * self.negative_electrode_coating_thickness_um
                * 1e-4
            ),
            3,
        )

    # Separator properties
    @computed_field(alias="Separator sheet count")
    def separator_sheet_count(self) -> int:
        return self.positive_electrode_sheet_count + 4

    @computed_field(alias="Separator sheet width [mm]")
    def separator_sheet_width_mm(self) -> float:
        return round(
            self.positive_electrode_sheet_width_mm
            + 4 * self.cell_electrode_overhang_mm,
            3,
        )

    @computed_field(alias="Separator sheet height [mm]")
    def separator_sheet_height_mm(self) -> float:
        return round(self.jelly_roll_height_mm, 3)

    # Electrolyte properties
    @computed_field(alias="Electrolyte mass [g]")
    def electrolyte_mass_g(self) -> float:
        return round(
            self.cell_nominal_capacity_Ah * 2, 3
        )  # Assuming 2 g of electrolyte per Ah

    # Validators

    @field_validator("cell_volume_packing_ratio")
    def validate_cell_volume_packing_ratio(cls, value: float) -> float:
        return cls._validate_range(value, CELL_MIN_VOLUME_PACKING_RATIO, CELL_MAX_VOLUME_PACKING_RATIO, "Cell volume packing ratio")

    @field_validator("cell_casing_thickness_mm")
    def validate_cell_casing_thickness(cls, value: float) -> float:
        return cls._validate_range(value, 0.5, 0.9, "Cell casing thickness")

    @field_validator(
        "positive_electrode_foil_thickness_um", "negative_electrode_foil_thickness_um"
    )
    def validate_foil_thickness(cls, value: float) -> float:
        return cls._validate_range(value, 5, float("inf"), "Foil thickness", "um")

    @field_validator("separator_thickness_um")
    def validate_separator_thickness(cls, value: float) -> float:
        return cls._validate_range(value, 10, 20, "Separator thickness")

    @field_validator(
        "negative_electrode_mass_loading_mg_cm2",
    )
    def validate_mass_loading(cls, value: float) -> float:
        return cls._validate_range(value, NEGATIVE_ELECTRODE_MASS_LOADING_MIN, NEGATIVE_ELECTRODE_MASS_LOADING_MAX, "Mass loading")

    @field_validator("positive_electrode_mass_loading_mg_cm2")
    def validate_positive_electrode_mass_loading(cls, value: float) -> float:
        return cls._validate_range(value, POSITIVE_ELECTRODE_MASS_LOADING_MIN, POSITIVE_ELECTRODE_MASS_LOADING_MAX, "Mass loading")

    @field_validator("positive_electrode_porosity")
    def validate_electrode_porosity(cls, value: float) -> float:
        return cls._validate_range(value, POSITIVE_ELECTRODE_POROSITY_MIN, POSITIVE_ELECTRODE_POROSITY_MAX, "Electrode porosity")

    @field_validator("negative_electrode_porosity")
    def validate_negative_electrode_porosity(cls, value: float) -> float:
        return cls._validate_range(value, NEGATIVE_ELECTRODE_POROSITY_MIN, NEGATIVE_ELECTRODE_POROSITY_MAX, "Electrode porosity")

    @field_validator(
        "positive_electrode_active_material_volume_fraction",
        "negative_electrode_active_material_volume_fraction",
    )
    def validate_electrode_active_material_volume_fraction(cls, value: float) -> float:
        return cls._validate_range(
            value, 0, 1, "Electrode active material volume fraction"
        )

    @model_validator(mode="after")
    def validate_porosity_and_active_material_sum(self) -> "CellDesign":
        pos = self._get_electrode_formulation("positive")
        neg = self._get_electrode_formulation("negative")
        pos_sum = (
            self.positive_electrode_porosity
            + self.positive_electrode_active_material_volume_fraction
        )
        neg_sum = (
            self.negative_electrode_porosity
            + self.negative_electrode_active_material_volume_fraction
        )
        if pos_sum > 1:
            MSG = "Positive electrode porosity + active material volume fraction sum exceeds 1.0."
            MSG += f" Set the positive electrode active material mass fraction, which is {self.positive_electrode_active_material_mass_fraction}, below {pos.electrode_formulation_density_g_cm3 / KNOWN_MATERIALS[pos.primary_active_material]['Density [g.cm-3]']}."
            raise ValueError(MSG)
        if neg_sum > 1:
            MSG = "Negative electrode porosity + active material volume fraction sum exceeds 1.0."
            MSG += f" Set the negative electrode active material mass fraction, which is {self.negative_electrode_active_material_mass_fraction}, below {neg.electrode_formulation_density_g_cm3 / KNOWN_MATERIALS[neg.primary_active_material]['Density [g.cm-3]']}."
            raise ValueError(MSG)
        return self

    @model_validator(mode="after")
    def validate_primary_electrode_formulation_name_matches_material(
        self,
    ) -> "CellDesign":
        """Validate that primary electrode formulation name contains similar string as primary active material name."""
        pos_form = self._get_electrode_formulation("positive")
        neg_form = self._get_electrode_formulation("negative")

        # Check positive electrode
        pos_name = pos_form.name.lower()
        pos_material = pos_form.primary_active_material.lower()

        # For blended materials (e.g., "Si5%+Graphite95%"), extract base materials
        if "+" in pos_material:
            pos_materials = [mat.strip() for mat in pos_material.split("+")]
            if not any(mat in pos_name for mat in pos_materials):
                raise ValueError(
                    f"Positive electrode formulation name '{pos_form.name}' must contain "
                    f"similar string as primary active material '{pos_form.primary_active_material}'"
                )
        else:
            if pos_material not in pos_name:
                raise ValueError(
                    f"Positive electrode formulation name '{pos_form.name}' must contain "
                    f"similar string as primary active material '{pos_form.primary_active_material}'"
                )

        # Check negative electrode
        neg_name = neg_form.name.lower()
        neg_material = neg_form.primary_active_material.lower()

        # For blended materials (e.g., "Si5%+Graphite95%"), extract base materials
        if "+" in neg_material:
            neg_materials = [mat.strip() for mat in neg_material.split("+")]
            if not any(mat in neg_name for mat in neg_materials):
                raise ValueError(
                    f"Negative electrode formulation name '{neg_form.name}' must contain "
                    f"similar string as primary active material '{neg_form.primary_active_material}'"
                )
        else:
            if neg_material not in neg_name:
                raise ValueError(
                    f"Negative electrode formulation name '{neg_form.name}' must contain "
                    f"similar string as primary active material '{neg_form.primary_active_material}'"
                )

        return self

    @model_validator(mode="after")
    def optimize_coating_thickness_after_validation(self) -> "CellDesign":
        """
        Automatically optimize coating thickness when mass loading or formulation changes
        to ensure coating density and porosity remain within validation limits.
        """
        try:
            # Check if we should optimize positive electrode
            pos_form = self._get_electrode_formulation("positive")
            if pos_form and hasattr(pos_form, "electrode_formulation_density_g_cm3"):
                # Get current values to check if they're within limits
                mass_loading = self.positive_electrode_mass_loading_mg_cm2
                coating_thickness = self.positive_electrode_coating_thickness_um

                # Calculate current density
                coating_density = (mass_loading * 1e-3) / (coating_thickness * 1e-4)
                # Note: optimize_electrode_coating_thickness already updates the attribute

                # Also check porosity
                formulation_density = pos_form.electrode_formulation_density_g_cm3
                if formulation_density > 0:
                    # Check if current density is outside limits (2.5-4.0 g/cm³)
                    if not (
                        0.63 * formulation_density
                        <= coating_density
                        <= 0.85 * formulation_density
                    ):
                        # Optimize coating thickness
                        self.optimize_electrode_coating_thickness("positive")
        except Exception:
            # If optimization fails, continue with original values
            pass

        try:
            # Check if we should optimize negative electrode
            neg_form = self._get_electrode_formulation("negative")
            if neg_form and hasattr(neg_form, "electrode_formulation_density_g_cm3"):
                mass_loading = self.negative_electrode_mass_loading_mg_cm2
                coating_thickness = self.negative_electrode_coating_thickness_um

                # Calculate coating density
                coating_density = (mass_loading * 1e-3) / (coating_thickness * 1e-4)

                # Also check porosity
                formulation_density = neg_form.electrode_formulation_density_g_cm3
                if formulation_density > 0:
                    if not (
                        0.63 * formulation_density
                        <= coating_density
                        <= 0.85 * formulation_density
                    ):
                        self.optimize_electrode_coating_thickness("negative")

        except Exception:
            # If optimization fails, continue with original values
            pass

        return self

    @field_validator("positive_electrode_active_material_volume_fraction")
    def validate_electrode_porosity_and_active_material(cls, value: float) -> float:
        return cls._validate_range(value, 0, 1, "Active material volume fraction")

    # Create a validator for separator areal density to ensure it is between 10 and 20 g.m-2
    @field_validator("separator_areal_density_g_m2")
    def validate_separator_areal_density(cls, value: float) -> float:
        if not (10 <= value <= 20):
            raise ValueError(f"Separator areal density is {value} but must be between 10 and 20 g.m-2")
        return value


# Define the design parameters for a prismatic cell
class PrismaticCellDesignParameters(CellDesign):
    form_factor: str = Field("Prismatic", alias="Form factor")
    cell_casing_material: dict = Field(
        Material("Aluminum").as_alias_dict(), alias="Cell casing material"
    )
    cell_width_mm: float = Field(225, alias="Cell width [mm]")
    cell_height_mm: float = Field(
        100, alias="Cell height [mm]"
    )  # Ensure this is always available

    # --- Computed fields for derived properties ---
    # Cell properties
    @computed_field(alias="Cell casing mass [g]")
    def cell_casing_mass_g(self) -> float:
        # Convert mm to cm
        height_cm = self.cell_height_mm * 0.1
        width_cm = self.cell_width_mm * 0.1
        thickness_cm = self.cell_thickness_mm * 0.1
        inner_width_cm = width_cm - 2 * (self.cell_casing_thickness_mm * 0.1)
        inner_thickness_cm = thickness_cm - 2 * (self.cell_casing_thickness_mm * 0.1)
        # Outer volume minus inner volume (hollow rectangular prism)
        outer_volume_cm3 = height_cm * width_cm * thickness_cm
        inner_volume_cm3 = height_cm * inner_width_cm * inner_thickness_cm
        volume_cm3 = outer_volume_cm3 - inner_volume_cm3
        mass_g = volume_cm3 * self.cell_casing_material["Density [g.cm-3]"]
        return round(mass_g, 3)

    @computed_field(alias="Cell thickness [mm]")
    def cell_thickness_mm(self) -> float:
        return round(
            self.jelly_roll_thickness_mm + 2 * self.cell_casing_thickness_mm, 3
        )

    @computed_field(alias="Cell cooling surface area [mm2]")
    def cell_cooling_surface_area_mm2(self) -> float:
        return round(self.cell_width_mm * self.cell_thickness_mm, 3)

    # Jelly roll properties
    @computed_field(alias="Jelly roll height [mm]")
    def jelly_roll_height_mm(self) -> float:
        return round(self.cell_height_mm * self.cell_volume_packing_ratio ** (1 / 2), 3)

    @computed_field(alias="Jelly roll width [mm]")
    def jelly_roll_width_mm(self) -> float:
        return round(self.cell_width_mm * self.cell_volume_packing_ratio ** (1 / 2), 3)

    @computed_field(alias="Jelly roll thickness [mm]")
    def jelly_roll_thickness_mm(self) -> float:
        pos_thickness = (
            (
                2 * self.positive_electrode_coating_thickness_um
                + self.positive_electrode_foil_thickness_um
            )
            * 1e-3
            * self.positive_electrode_sheet_count
        )
        neg_thickness = (
            (
                2 * self.negative_electrode_coating_thickness_um
                + self.negative_electrode_foil_thickness_um
            )
            * 1e-3
            * self.negative_electrode_sheet_count
        )
        sep_thickness = self.separator_thickness_um * 1e-3 * self.separator_sheet_count
        return round(pos_thickness + neg_thickness + sep_thickness, 3)

    @computed_field(alias="Jelly roll mass [g]")
    def jelly_roll_mass_g(self) -> float:
        pos_mass = (
            (
                2
                * self.positive_electrode_coating_thickness_um
                * 1e-4
                * self.positive_electrode_coating_density_g_cm3
                + self.positive_electrode_foil_thickness_um
                * 1e-4
                * self.positive_electrode_foil_density_g_cm3
            )
            * self.positive_electrode_sheet_count
            * self.positive_electrode_sheet_height_mm
            * self.positive_electrode_sheet_width_mm
            * 1e-2
        )
        neg_mass = (
            (
                2
                * self.negative_electrode_coating_thickness_um
                * 1e-4
                * self.negative_electrode_coating_density_g_cm3
                + self.negative_electrode_foil_thickness_um
                * 1e-4
                * self.negative_electrode_foil_density_g_cm3
            )
            * self.negative_electrode_sheet_count
            * self.negative_electrode_sheet_height_mm
            * self.negative_electrode_sheet_width_mm
            * 1e-2
        )
        separator_mass = (
            (self.separator_areal_density_g_m2)
            * self.separator_sheet_count
            * self.separator_sheet_height_mm
            * self.separator_sheet_width_mm
            * 1e-6
        )
        return round(pos_mass + neg_mass + separator_mass, 3)

    # -- Electrode properties --
    # Derived from base properties

    @computed_field(alias="Positive electrode sheet height [mm]")
    def positive_electrode_sheet_height_mm(self) -> float:
        return round(self.jelly_roll_height_mm - 4 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Positive electrode sheet width [mm]")
    def positive_electrode_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm - 4 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Negative electrode sheet height [mm]")
    def negative_electrode_sheet_height_mm(self) -> float:
        return self.jelly_roll_height_mm - 2 * self.cell_electrode_overhang_mm

    @computed_field(alias="Negative electrode sheet width [mm]")
    def negative_electrode_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm - 2 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Separator sheet height [mm]")
    def separator_sheet_height_mm(self) -> float:
        return self.jelly_roll_height_mm

    @computed_field(alias="Separator sheet width [mm]")
    def separator_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm, 3)


class CylindricalCellDesignParameters(CellDesign):
    form_factor: str = Field("Cylindrical", alias="Form factor")
    cell_casing_material: dict = Field(
        Material("Steel").as_alias_dict(), alias="Cell casing material"
    )
    cell_diameter_mm: float = Field(21, alias="Cell diameter [mm]")
    cell_height_mm: float = Field(70, alias="Cell height [mm]")
    cell_volume_packing_ratio: float = Field(0.98, alias="Cell volume packing ratio")
    cell_casing_thickness_mm: float = Field(0.4, alias="Cell casing thickness [mm]")
    cell_cooling_arc_degree: float = Field(30, alias="Cell cooling arc [degree]")
    cell_cooling_channel_height_mm: float = Field(
        45.5, alias="Cell cooling channel height [mm]"
    )
    cell_thermal_resistance_K_W: float = Field(
        2, alias="Cell thermal resistance [K.W-1]"
    )
    positive_electrode_sheet_count: int = Field(
        1, alias="Positive electrode sheet count"
    )
    jelly_roll_inner_diameter_mm: float = Field(
        4, alias="Jelly roll inner diameter [mm]"
    )

    @field_validator("positive_electrode_sheet_count")
    @classmethod
    def check_positive_electrode_sheet_count(cls, v):
        return cls._validate_range(
            v, 0, 1, "Positive electrode sheet count (cylindrical)"
        )

    @field_validator("cell_casing_material", mode="before")
    @classmethod
    def convert_material(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            return Material.from_name(v.capitalize())
        raise TypeError("Cell casing material must be a Material or string")

    @computed_field(alias="Cell casing mass [g]")
    def cell_casing_mass_g(self) -> float:
        # Convert mm to cm
        height_cm = self.cell_height_mm * 0.1
        outer_radius_cm = (self.cell_diameter_mm / 2) * 0.1
        inner_radius_cm = outer_radius_cm - (self.cell_casing_thickness_mm * 0.1)
        volume_cm3 = np.pi * height_cm * (outer_radius_cm**2 - inner_radius_cm**2)

        mass_g = volume_cm3 * self.cell_casing_material["Density [g.cm-3]"]
        return round(mass_g, 3)

    @computed_field(alias="Cell cooling surface area [mm2]")
    def cell_cooling_surface_area_mm2(self) -> float:
        return round(
            (
                np.pi
                * self.cell_cooling_arc_degree
                / 180
                * self.cell_diameter_mm
                / 2
                * self.cell_cooling_channel_height_mm
            ),
            3,
        )

    @computed_field(alias="Cell volume [L]")
    def cell_volume_L(self) -> float:
        # Calculate cell volume based on height and diameter
        return round(
            np.pi * (self.cell_diameter_mm / 2) ** 2 * self.cell_height_mm * 1e-6, 3
        )

    @computed_field(alias="Jelly roll height [mm]")
    def jelly_roll_height_mm(self) -> float:
        return round(self.cell_height_mm * self.cell_volume_packing_ratio, 3)

    @computed_field(alias="Jelly roll outer diameter [mm]")
    def jelly_roll_outer_diameter_mm(self) -> float:
        return round(self.cell_diameter_mm - 2 * self.cell_casing_thickness_mm - 0.1, 3)

    @computed_field(alias="Jelly roll windings")
    def jelly_roll_windings(self) -> int:
        # Calculate the number of windings based on the jelly roll height and wrapping thickness
        pos_electrode_thickness_mm = (
            2 * self.positive_electrode_coating_thickness_um * 1e-3
            + self.positive_electrode_foil_thickness_um * 1e-3
        ) * self.positive_electrode_sheet_count  # Convert um to mm
        neg_electrode_thickness_mm = (
            2 * self.negative_electrode_coating_thickness_um * 1e-3
            + self.negative_electrode_foil_thickness_um * 1e-3
        ) * self.negative_electrode_sheet_count  # Convert um to mm
        separator_thickness_mm = (
            2 * self.separator_thickness_um * 1e-3
        )  # Convert um to mm

        layer_thickness_mm = (
            pos_electrode_thickness_mm
            + neg_electrode_thickness_mm
            + separator_thickness_mm
        )
        return int(
            (
                self.jelly_roll_outer_diameter_mm / 2
                - self.jelly_roll_inner_diameter_mm / 2
                - self.jelly_roll_wrapping_thickness_mm
            )
            / layer_thickness_mm
        )

    @computed_field(alias="Jelly roll wrapping thickness [mm]")
    def jelly_roll_wrapping_thickness_mm(self) -> float:
        pos_electrode_thickness_mm = (
            2 * self.positive_electrode_coating_thickness_um * 1e-3
            + self.positive_electrode_foil_thickness_um * 1e-3
        ) * self.positive_electrode_sheet_count  # Convert um to mm
        neg_electrode_thickness_mm = (
            2 * self.negative_electrode_coating_thickness_um * 1e-3
            + self.negative_electrode_foil_thickness_um * 1e-3
        ) * self.negative_electrode_sheet_count  # Convert um to mm
        separator_thickness_mm = (
            2 * self.separator_thickness_um * 1e-3
        )  # Convert um to mm

        layer_thickness_mm = (
            pos_electrode_thickness_mm
            + neg_electrode_thickness_mm
            + separator_thickness_mm
        )
        # Calculate the jelly roll wrapping thickness based on the number of windings and the total height
        a = (
            self.jelly_roll_outer_diameter_mm / 2
            - self.jelly_roll_inner_diameter_mm / 2
        ) / layer_thickness_mm

        return round((a - int(a)) * layer_thickness_mm, 3)  # Convert to mm

    @computed_field(alias="Jelly roll mass [g]")
    def jelly_roll_mass_g(self) -> float:
        pos_electrode_sheet_area_mm2 = (
            self.positive_electrode_sheet_height_mm
            * self.positive_electrode_sheet_width_mm
        )
        neg_electrode_sheet_area_mm2 = (
            self.negative_electrode_sheet_height_mm
            * self.negative_electrode_sheet_width_mm
        )
        separator_area_mm2 = (
            self.separator_sheet_height_mm * self.separator_sheet_width_mm
        )
        # Calculate jelly roll mass based on area and mass loading
        pos_mass = (
            (
                self.positive_electrode_mass_loading_mg_cm2
                * 1e-3  # Convert mg.cm-2 to g.cm-2
                + self.positive_electrode_coating_density_g_cm3
                * self.positive_electrode_coating_thickness_um
                * 1e-4  # Convert um to cm
                + self.positive_electrode_foil_density_g_cm3
                * self.positive_electrode_foil_thickness_um
                * 1e-4  # Convert um to cm
            )
            * pos_electrode_sheet_area_mm2
            * 1e-2
            * self.positive_electrode_sheet_count
        )
        neg_mass = (
            (
                self.negative_electrode_mass_loading_mg_cm2
                * 1e-3  # Convert mg.cm-2 to g.cm-2
                + self.negative_electrode_coating_density_g_cm3
                * self.negative_electrode_coating_thickness_um
                * 1e-4  # Convert um to cm
                + self.negative_electrode_foil_density_g_cm3
                * self.negative_electrode_foil_thickness_um
                * 1e-4  # Convert um to cm
            )
            * neg_electrode_sheet_area_mm2
            * 1e-2
            * self.negative_electrode_sheet_count
        )
        separator_mass = (
            self.separator_areal_density_g_m2
            * separator_area_mm2
            * 1e-6
            * self.separator_sheet_count
        )
        return round(pos_mass + neg_mass + separator_mass, 3)

    @computed_field(alias="Jelly roll volume [L]")
    def jelly_roll_volume_L(self) -> float:
        return round(
            (
                (
                    self.jelly_roll_outer_diameter_mm**2
                    - self.jelly_roll_inner_diameter_mm**2
                )
                * self.jelly_roll_height_mm
                * np.pi
                / 4
                * 1e-6
            ),
            3,
        )  # Convert mm3 to L

    # Positive electrode properties
    @computed_field(alias="Positive electrode sheet width [mm]")
    def positive_electrode_sheet_width_mm(self) -> float:
        pos_electrode_thickness_mm = (
            2 * self.positive_electrode_coating_thickness_um * 1e-3
            + self.positive_electrode_foil_thickness_um * 1e-3
        ) * self.positive_electrode_sheet_count  # Convert um to mm
        neg_electrode_thickness_mm = (
            2 * self.negative_electrode_coating_thickness_um * 1e-3
            + self.negative_electrode_foil_thickness_um * 1e-3
        ) * self.negative_electrode_sheet_count  # Convert um to mm
        separator_thickness_mm = (
            2 * self.separator_thickness_um * 1e-3
        )  # Convert um to mm

        layer_thickness_mm = (
            pos_electrode_thickness_mm
            + neg_electrode_thickness_mm
            + separator_thickness_mm
        )
        return round(
            (
                (
                    self.jelly_roll_outer_diameter_mm**2
                    - self.jelly_roll_inner_diameter_mm**2
                )
                * np.pi
                / 4
                / layer_thickness_mm
            ),
            3,
        )

    @computed_field(alias="Negative electrode sheet count")
    def negative_electrode_sheet_count(self) -> float:
        return self.positive_electrode_sheet_count

    @computed_field(alias="Negative electrode sheet width [mm]")
    def negative_electrode_sheet_width_mm(self) -> float:
        return (
            self.positive_electrode_sheet_width_mm + 2 * self.cell_electrode_overhang_mm
        )

    @computed_field(alias="Separator sheet width [mm]")
    def separator_sheet_width_mm(self) -> float:
        return (
            self.positive_electrode_sheet_width_mm + 4 * self.cell_electrode_overhang_mm
        )

    @computed_field(alias="Separator sheet count")
    def separator_sheet_count(self) -> int:
        return self.positive_electrode_sheet_count + 1

    @model_validator(mode="after")
    def validate_cell_cooling_channel_height(self) -> "CylindricalCellDesignParameters":
        if self.cell_cooling_channel_height_mm > 0.9 * self.cell_height_mm:
            raise ValueError(
                f"Cell cooling channel height is {self.cell_cooling_channel_height_mm} but must be less than 90% of cell height that is <= {0.9 * self.cell_height_mm}"
            )
        return self

    @field_validator("cell_casing_thickness_mm")
    def validate_cell_casing_thickness(cls, value: float) -> float:
        return cls._validate_range(value, 0.3, 0.7, "Cell casing thickness")


class PouchCellDesignParameters(CellDesign):
    form_factor: str = Field("Pouch", alias="Form factor")
    cell_casing_material: dict = Field(
        Material("Aluminum-Laminate").as_alias_dict(), alias="Cell casing material"
    )
    cell_casing_thickness_mm: float = Field(0.150, alias="Cell casing thickness [mm]")
    cell_volume_packing_ratio: float = Field(0.95, alias="Cell volume packing ratio")
    cell_width_mm: float = Field(100, alias="Cell width [mm]")
    cell_height_mm: float = Field(150, alias="Cell height [mm]")

    @computed_field(alias="Cell thickness [mm]")
    def cell_thickness_mm(self) -> float:
        return round(
            self.jelly_roll_thickness_mm + 2 * self.cell_casing_thickness_mm, 3
        )

    @computed_field(alias="Cell casing mass [g]")
    def cell_casing_mass_g(self) -> float:
        # Convert mm to cm
        height_cm = self.cell_height_mm * 0.1
        width_cm = self.cell_width_mm * 0.1
        thickness_cm = self.cell_thickness_mm * 0.1
        casing_thickness_cm = self.cell_casing_thickness_mm * 0.1
        volume_cm3 = (
            (height_cm * width_cm + height_cm * thickness_cm + width_cm * thickness_cm)
            * 2
            * casing_thickness_cm
        )
        mass_g = volume_cm3 * self.cell_casing_material["Density [g.cm-3]"]
        return round(mass_g, 3)

    @computed_field(alias="Cell cooling surface area [mm2]")
    def cell_cooling_surface_area_mm2(self) -> float:
        return round(self.cell_width_mm * self.cell_height_mm, 3)

    @computed_field(alias="Cell volume [L]")
    def cell_volume_L(self) -> float:
        # Calculate cell volume based on height and width
        return round(
            self.cell_height_mm * self.cell_width_mm * self.cell_thickness_mm * 1e-6,
            3,
        )  # mm3 to L

    @computed_field(alias="Jelly roll height [mm]")
    def jelly_roll_height_mm(self) -> float:
        return round(self.cell_height_mm * self.cell_volume_packing_ratio ** (1 / 2), 3)

    @computed_field(alias="Jelly roll width [mm]")
    def jelly_roll_width_mm(self) -> float:
        return round(self.cell_width_mm * self.cell_volume_packing_ratio ** (1 / 2), 3)

    @computed_field(alias="Jelly roll thickness [mm]")
    def jelly_roll_thickness_mm(self) -> float:
        pos_thickness = (
            (
                2 * self.positive_electrode_coating_thickness_um
                + self.positive_electrode_foil_thickness_um
            )
            * 1e-3
            * self.positive_electrode_sheet_count
        )
        neg_thickness = (
            (
                2 * self.negative_electrode_coating_thickness_um
                + self.negative_electrode_foil_thickness_um
            )
            * 1e-3
            * self.negative_electrode_sheet_count
        )
        sep_thickness = self.separator_thickness_um * 1e-3 * self.separator_sheet_count
        return round(pos_thickness + neg_thickness + sep_thickness, 3)

    @computed_field(alias="Jelly roll mass [g]")
    def jelly_roll_mass_g(self) -> float:
        pos_mass = (
            (
                2
                * self.positive_electrode_coating_thickness_um
                * 1e-4
                * self.positive_electrode_coating_density_g_cm3
                + self.positive_electrode_foil_thickness_um
                * 1e-4
                * self.positive_electrode_foil_density_g_cm3
            )
            * self.positive_electrode_sheet_count
            * self.positive_electrode_sheet_height_mm
            * self.positive_electrode_sheet_width_mm
            * 1e-2
        )
        neg_mass = (
            (
                2
                * self.negative_electrode_coating_thickness_um
                * 1e-4
                * self.negative_electrode_coating_density_g_cm3
                + self.negative_electrode_foil_thickness_um
                * 1e-4
                * self.negative_electrode_foil_density_g_cm3
            )
            * self.negative_electrode_sheet_count
            * self.negative_electrode_sheet_height_mm
            * self.negative_electrode_sheet_width_mm
            * 1e-2
        )
        separator_mass = (
            (self.separator_areal_density_g_m2)
            * self.separator_sheet_count
            * self.separator_sheet_height_mm
            * self.separator_sheet_width_mm
            * 1e-6
        )
        return round(pos_mass + neg_mass + separator_mass, 3)

    # -- Electrode properties --
    # Derived from base properties

    @computed_field(alias="Positive electrode sheet height [mm]")
    def positive_electrode_sheet_height_mm(self) -> float:
        return round(self.jelly_roll_height_mm - 4 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Positive electrode sheet width [mm]")
    def positive_electrode_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm - 4 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Negative electrode sheet height [mm]")
    def negative_electrode_sheet_height_mm(self) -> float:
        return self.jelly_roll_height_mm - 2 * self.cell_electrode_overhang_mm

    @computed_field(alias="Negative electrode sheet width [mm]")
    def negative_electrode_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm - 2 * self.cell_electrode_overhang_mm, 3)

    @computed_field(alias="Separator sheet height [mm]")
    def separator_sheet_height_mm(self) -> float:
        return self.jelly_roll_height_mm

    @computed_field(alias="Separator sheet width [mm]")
    def separator_sheet_width_mm(self) -> float:
        return round(self.jelly_roll_width_mm, 3)

    # Functions to validate ranges
    @field_validator("cell_casing_thickness_mm")
    def validate_cell_casing_thickness(cls, value: float) -> float:
        return cls._validate_range(value, 0.1, 0.3, "Cell casing thickness")
