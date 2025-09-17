from typing import TypedDict, NotRequired, Required

ElectrolyteCompositionParameters = TypedDict("ElectrolyteCompositionParameters", {
    "name": Required[str],
    "Primary solvent": Required[str],
    "Secondary solvent": NotRequired[str],
    "Tertiary solvent": NotRequired[str],
    "Primary solvent volume fraction": Required[float],
    "Secondary solvent volume fraction": NotRequired[float],
    "Tertiary solvent volume fraction": NotRequired[float],
    "Primary salt": Required[str],
    "Secondary salt": NotRequired[str],
    "Tertiary salt": NotRequired[str],
    "Primary salt concentration [mol.L-1]": Required[float],
    "Secondary salt concentration [mol.L-1]": NotRequired[float],
    "Tertiary salt concentration [mol.L-1]": NotRequired[float],
    "Primary additive": NotRequired[str],
    "Secondary additive": NotRequired[str],
    "Tertiary additive": NotRequired[str],
    "Primary additive mass fraction": NotRequired[float],
    "Secondary additive mass fraction": NotRequired[float],
    "Tertiary additive mass fraction": NotRequired[float],
})
class ElectrolyteComposition(ElectrolyteCompositionParameters, total=False):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["name"] = "EC:EMC:DMC (2:4:4)"
        self["Primary solvent"] = "EC"
        self["Secondary solvent"] = "EMC"
        self["Tertiary solvent"] = "DMC"
        self["Primary solvent volume fraction"] = 0.2
        self["Secondary solvent volume fraction"] = 0.4
        self["Tertiary solvent volume fraction"] = 0.4
        self["Primary salt"] = "LiPF6"
        self["Primary salt concentration [mol.L-1]"] = 1.0
