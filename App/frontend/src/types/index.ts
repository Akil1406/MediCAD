export type DeviceType =
  | 'tube'
  | 'catheter'
  | 'tapered_tube'
  | 'connector'
  | 'injector'
  | 'plunger'
  | 'assembly';

export interface BoundingBox {
  min_x: number;
  max_x: number;
  min_y: number;
  max_y: number;
  min_z: number;
  max_z: number;
}

export interface CADProperties {
  device_type: string;
  template_name: string;
  template_version: string;
  solid_count: number;
  is_watertight: boolean;
  volume_mm3: number;
  surface_area_mm2: number;
  bounding_box: BoundingBox;
  derived_parameters: Record<string, any>;
  warnings: string[];
}

export interface ValidationIssue {
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'BLOCKED';
  code: string;
  message: string;
  parameter?: string;
  suggested_fix?: string;
  measured_value?: number;
  threshold_value?: number;
}

export interface ValidationReport {
  passed: boolean;
  device_type: string;
  solid_valid: boolean;
  wall_thickness_mm?: number;
  total_volume_mm3?: number;
  total_surface_area_mm2?: number;
  aspect_ratio?: number;
  issues: ValidationIssue[];
  timestamp?: string;
}

export interface Material {
  material_id: string;
  name: string;
  common_trade_names: string[];
  family: 'polymer' | 'metal' | 'elastomer' | 'composite';
  category: string;
  density_g_cm3: number;
  tensile_strength_mpa: number;
  yield_strength_mpa?: number;
  elastic_modulus_mpa: number;
  flexural_modulus_mpa?: number;
  elongation_at_break_pct?: number;
  shore_hardness?: string;
  temperature_min_c: number;
  temperature_max_c: number;
  manufacturing_methods: string[];
  sterilization_compatibility: Record<string, string>;
  chemical_resistance: string[];
  iso_10993_biocompatibility_reference: string;
  typical_medical_applications: string[];
  source: string;
  source_reference: string;
  data_retrieval_date: string;
}

export interface CandidateScore {
  material: Material;
  score: number;
  engineering_fit: 'Excellent' | 'Good' | 'Moderate' | 'Low';
  matched_criteria: string[];
  unmatched_criteria: string[];
  sterilization_note: string;
  engineering_notes: string;
  evidence_provenance: string;
  regulatory_disclaimer: string;
}

export interface MaterialRequirements {
  minimum_tensile_strength_mpa?: number;
  minimum_elastic_modulus_mpa?: number;
  maximum_elastic_modulus_mpa?: number;
  max_operating_temp_c?: number;
  preferred_manufacturing_method?: string;
  required_sterilization_method?: string;
  flexibility_preference?: 'rigid' | 'semi_rigid' | 'flexible' | 'elastomeric' | 'any';
}

export interface DesignSummary {
  design_id: string;
  title: string;
  device_type: string;
  created_at_utc: string;
  latest_version: number;
}

export interface DesignVersion {
  version_id: string;
  design_id: string;
  version_number: number;
  user_prompt: string;
  device_type: string;
  specification_json: Record<string, any> | string;
  cad_properties_json: CADProperties | string;
  validation_json: ValidationReport | string;
  material_candidates_json: CandidateScore[] | string;
  export_paths_json: Record<string, string> | string;
  created_at_utc: string;
  app_version: string;
}

export interface SimulationResult {
  simulation_type: string;
  material_name?: string;
  status: 'PASS' | 'WARNING' | 'FAIL';
  solver_notes?: string;
  yield_safety_factor?: number;
  hoop_stress_mpa?: number;
  theoretical_burst_pressure_bar?: number;
  critical_buckling_load_n?: number;
  critical_buckling_load_gf?: number;
  buckling_safety_factor?: number;
  total_thumb_force_n?: number;
  total_thumb_force_kgf?: number;
  pressure_drop_nozzle_bar?: number;
  ergonomic_assessment?: string;
  assumptions?: string[];
}
