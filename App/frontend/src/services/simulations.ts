import { request } from './api';
import { SimulationResult } from '../types';

export interface SimulationPayload {
  simulation_type: 'burst_pressure' | 'column_buckling' | 'syringe_dispense_force';
  material_id: string;
  operating_pressure_bar?: number;
  axial_push_force_n?: number;
  dispense_flow_rate_ml_s?: number;
  fluid_viscosity_cp?: number;
  needle_gauge_g?: number;
  needle_length_mm?: number;
  custom_dimensions?: Record<string, number>;
}

export async function runSimulation(payload: SimulationPayload): Promise<{ simulation: SimulationResult }> {
  return request<{ simulation: SimulationResult }>('/simulations', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
