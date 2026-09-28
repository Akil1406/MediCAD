import { request } from './api';
import { Material, CandidateScore, MaterialRequirements } from '../types';

export async function listMaterials(): Promise<{ materials: Material[] }> {
  return request<{ materials: Material[] }>('/materials');
}

export async function rankMaterials(requirements: MaterialRequirements): Promise<{ candidates: CandidateScore[] }> {
  return request<{ candidates: CandidateScore[] }>('/materials/rank', {
    method: 'POST',
    body: JSON.stringify(requirements),
  });
}
