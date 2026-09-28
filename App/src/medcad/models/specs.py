"""Parametric device specifications with strict validation."""

from pydantic import BaseModel, Field, model_validator
from typing import Literal
import math
from .base import BaseSpec


class TubeSpec(BaseSpec):
    """Specification for a straight hollow tube."""
    device_type: Literal["tube"] = "tube"
    length_mm: float = Field(gt=0, description="Overall length of the tube in mm")
    outer_diameter_mm: float = Field(gt=0, description="Outer diameter (OD) in mm")
    inner_diameter_mm: float = Field(gt=0, description="Inner diameter (ID) in mm")

    @model_validator(mode="after")
    def validate_diameters(self) -> "TubeSpec":
        if self.inner_diameter_mm >= self.outer_diameter_mm:
            raise ValueError(
                f"Inner diameter ({self.inner_diameter_mm} mm) must be strictly less than "
                f"outer diameter ({self.outer_diameter_mm} mm)."
            )
        return self

    @property
    def wall_thickness_mm(self) -> float:
        return (self.outer_diameter_mm - self.inner_diameter_mm) / 2.0

    @property
    def outer_radius_mm(self) -> float:
        return self.outer_diameter_mm / 2.0

    @property
    def inner_radius_mm(self) -> float:
        return self.inner_diameter_mm / 2.0

    @property
    def cross_sectional_area_mm2(self) -> float:
        return math.pi * (self.outer_radius_mm**2 - self.inner_radius_mm**2)

    @property
    def lumen_volume_mm3(self) -> float:
        return math.pi * (self.inner_radius_mm**2) * self.length_mm

    @property
    def material_volume_mm3(self) -> float:
        return self.cross_sectional_area_mm2 * self.length_mm


class CatheterSpec(BaseSpec):
    """Specification for a catheter shaft with atraumatic tip and optional hub."""
    device_type: Literal["catheter"] = "catheter"
    length_mm: float = Field(gt=0, description="Total catheter working length in mm")
    outer_diameter_mm: float = Field(gt=0, description="Outer diameter of main shaft in mm")
    inner_diameter_mm: float = Field(gt=0, description="Inner diameter / lumen diameter in mm")
    tip_length_mm: float = Field(gt=0, description="Length of distal tapered/beveled tip in mm")
    tip_outer_diameter_mm: float | None = Field(default=None, description="Distal tip OD (defaults to 0.8*OD)")
    tip_angle_deg: float = Field(default=0.0, ge=0.0, le=90.0, description="Tip bevel or curve angle in degrees")
    has_luer_hub: bool = Field(default=True, description="Whether to include a proximal luer connection hub")
    hub_length_mm: float = Field(default=15.0, gt=0, description="Proximal hub length in mm")

    @model_validator(mode="after")
    def validate_catheter(self) -> "CatheterSpec":
        if self.inner_diameter_mm >= self.outer_diameter_mm:
            raise ValueError(
                f"Inner diameter ({self.inner_diameter_mm} mm) must be strictly less than "
                f"outer diameter ({self.outer_diameter_mm} mm)."
            )
        if self.tip_length_mm >= self.length_mm:
            raise ValueError(
                f"Tip length ({self.tip_length_mm} mm) cannot be greater than or equal to "
                f"total catheter length ({self.length_mm} mm)."
            )
        if self.tip_outer_diameter_mm is not None:
            if self.tip_outer_diameter_mm <= self.inner_diameter_mm:
                raise ValueError(
                    f"Tip outer diameter ({self.tip_outer_diameter_mm} mm) must be strictly greater than "
                    f"inner diameter ({self.inner_diameter_mm} mm)."
                )
            if self.tip_outer_diameter_mm > self.outer_diameter_mm:
                raise ValueError(
                    f"Tip outer diameter ({self.tip_outer_diameter_mm} mm) cannot exceed "
                    f"shaft outer diameter ({self.outer_diameter_mm} mm)."
                )
        return self

    @property
    def effective_tip_od_mm(self) -> float:
        if self.tip_outer_diameter_mm is not None:
            return self.tip_outer_diameter_mm
        # Default to a gentle 85% taper if tip_length > 0
        return max(self.inner_diameter_mm + 0.1, self.outer_diameter_mm * 0.85)

    @property
    def shaft_wall_thickness_mm(self) -> float:
        return (self.outer_diameter_mm - self.inner_diameter_mm) / 2.0

    @property
    def french_size(self) -> float:
        """French scale (Fr) = Outer Diameter in mm * 3."""
        return self.outer_diameter_mm * 3.0


class TaperedTubeSpec(BaseSpec):
    """Specification for a tapered shaft (e.g. dilatators, introducers)."""
    device_type: Literal["tapered_tube"] = "tapered_tube"
    length_mm: float = Field(gt=0, description="Total length in mm")
    proximal_outer_diameter_mm: float = Field(gt=0, description="Proximal outer diameter in mm")
    distal_outer_diameter_mm: float = Field(gt=0, description="Distal outer diameter in mm")
    inner_diameter_mm: float = Field(gt=0, description="Inner lumen diameter in mm")

    @model_validator(mode="after")
    def validate_taper(self) -> "TaperedTubeSpec":
        min_od = min(self.proximal_outer_diameter_mm, self.distal_outer_diameter_mm)
        if self.inner_diameter_mm >= min_od:
            raise ValueError(
                f"Inner diameter ({self.inner_diameter_mm} mm) must be less than the minimum outer diameter ({min_od} mm)."
            )
        return self

    @property
    def min_wall_thickness_mm(self) -> float:
        min_od = min(self.proximal_outer_diameter_mm, self.distal_outer_diameter_mm)
        return (min_od - self.inner_diameter_mm) / 2.0

    @property
    def max_wall_thickness_mm(self) -> float:
        max_od = max(self.proximal_outer_diameter_mm, self.distal_outer_diameter_mm)
        return (max_od - self.inner_diameter_mm) / 2.0


class ConnectorSpec(BaseSpec):
    """Specification for ISO standard Luer lock / slip connector."""
    device_type: Literal["connector"] = "connector"
    connector_type: Literal["male_luer", "female_luer", "barbed_connector"] = "male_luer"
    length_mm: float = Field(default=20.0, gt=0, description="Overall connector length in mm")
    outer_diameter_mm: float = Field(default=6.5, gt=0, description="Main body outer diameter in mm")
    inner_diameter_mm: float = Field(default=2.5, gt=0, description="Fluid passage inner diameter in mm")
    barb_count: int = Field(default=2, ge=0, le=6, description="Number of retention barbs")
    luer_taper_ratio: float = Field(default=0.06, gt=0, le=0.1, description="Standard 6% ISO Luer taper")

    @model_validator(mode="after")
    def validate_connector(self) -> "ConnectorSpec":
        if self.inner_diameter_mm >= self.outer_diameter_mm:
            raise ValueError("Inner diameter must be strictly less than outer diameter.")
        return self

    @property
    def wall_thickness_mm(self) -> float:
        return (self.outer_diameter_mm - self.inner_diameter_mm) / 2.0


class InjectorSpec(BaseSpec):
    """Specification for an injector / syringe barrel body."""
    device_type: Literal["injector"] = "injector"
    body_length_mm: float = Field(gt=0, description="Length of syringe barrel in mm")
    body_outer_diameter_mm: float = Field(gt=0, description="Barrel outer diameter in mm")
    body_inner_diameter_mm: float = Field(gt=0, description="Barrel inner diameter / bore in mm")
    nozzle_length_mm: float = Field(default=10.0, gt=0, description="Nozzle / luer tip length in mm")
    nozzle_outer_diameter_mm: float = Field(default=4.0, gt=0, description="Nozzle outer diameter in mm")
    nozzle_inner_diameter_mm: float = Field(default=1.8, gt=0, description="Nozzle orifice inner diameter in mm")
    flange_width_mm: float = Field(default=24.0, gt=0, description="Finger grip flange width in mm")
    flange_thickness_mm: float = Field(default=2.5, gt=0, description="Finger grip flange thickness in mm")

    @model_validator(mode="after")
    def validate_injector(self) -> "InjectorSpec":
        if self.body_inner_diameter_mm >= self.body_outer_diameter_mm:
            raise ValueError(
                f"Barrel inner diameter ({self.body_inner_diameter_mm} mm) must be less than "
                f"barrel outer diameter ({self.body_outer_diameter_mm} mm)."
            )
        if self.nozzle_inner_diameter_mm >= self.nozzle_outer_diameter_mm:
            raise ValueError(
                f"Nozzle inner diameter ({self.nozzle_inner_diameter_mm} mm) must be less than "
                f"nozzle outer diameter ({self.nozzle_outer_diameter_mm} mm)."
            )
        if self.flange_width_mm <= self.body_outer_diameter_mm:
            raise ValueError(
                f"Flange width ({self.flange_width_mm} mm) must be larger than barrel OD ({self.body_outer_diameter_mm} mm)."
            )
        return self

    @property
    def barrel_wall_thickness_mm(self) -> float:
        return (self.body_outer_diameter_mm - self.body_inner_diameter_mm) / 2.0

    @property
    def nozzle_wall_thickness_mm(self) -> float:
        return (self.nozzle_outer_diameter_mm - self.nozzle_inner_diameter_mm) / 2.0

    @property
    def usable_volume_ml(self) -> float:
        """Internal volumetric capacity in milliliters (cm3)."""
        radius_cm = (self.body_inner_diameter_mm / 2.0) / 10.0
        length_cm = self.body_length_mm / 10.0
        return math.pi * (radius_cm**2) * length_cm


class PlungerSpec(BaseSpec):
    """Specification for a syringe plunger mating component."""
    device_type: Literal["plunger"] = "plunger"
    plunger_length_mm: float = Field(gt=0, description="Total length of plunger rod in mm")
    rod_diameter_mm: float = Field(gt=0, description="Main cruciform / rod core diameter in mm")
    head_outer_diameter_mm: float = Field(gt=0, description="Piston / stopper sealing head diameter in mm")
    head_length_mm: float = Field(default=8.0, gt=0, description="Length of piston head in mm")
    thumb_rest_diameter_mm: float = Field(default=18.0, gt=0, description="Thumb press disc diameter in mm")
    thumb_rest_thickness_mm: float = Field(default=2.0, gt=0, description="Thumb press disc thickness in mm")
    rib_count: int = Field(default=2, ge=1, le=4, description="Number of sealing ring ribs")

    @model_validator(mode="after")
    def validate_plunger(self) -> "PlungerSpec":
        if self.rod_diameter_mm >= self.head_outer_diameter_mm:
            raise ValueError("Plunger rod diameter must be less than sealing head outer diameter.")
        if self.head_length_mm >= self.plunger_length_mm:
            raise ValueError("Head length cannot be greater than or equal to overall plunger length.")
        return self


class AssemblySpec(BaseSpec):
    """Specification for a multi-component assembled device."""
    device_type: Literal["assembly"] = "assembly"
    assembly_name: str = "Syringe_Plunger_Assembly"
    injector_spec: InjectorSpec
    plunger_spec: PlungerSpec
    radial_clearance_mm: float = Field(default=0.05, description="Designed radial clearance between barrel bore and plunger head")


class DesignRequest(BaseModel):
    """Structured intake request from user natural language or UI form."""
    prompt: str = Field(description="Raw user intent prompt")
    device_type: str = Field(description="Target device category")
    target_dimensions: dict[str, float] = Field(default_factory=dict)
    units: Literal["mm", "in"] = "mm"
    target_material_requirements: list[str] = Field(default_factory=list)
    manufacturing_preference: str | None = None
    target_clinical_context: str = Field(default="", description="Contextual note (e.g. vascular, subcutaneous)")
