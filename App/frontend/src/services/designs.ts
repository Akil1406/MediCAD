import { request } from './api';
import { DesignSummary, DesignVersion, ValidationReport, CandidateScore } from '../types';

export interface CreateDesignPayload {
  title: string;
  device_type: string;
  prompt?: string;
  dimensions?: Record<string, number>;
  units?: 'mm' | 'in';
}

export interface ParameterUpdatePayload {
  parameters: Record<string, any>;
  prompt?: string;
}

export async function listDesigns(): Promise<{ designs: DesignSummary[] }> {
  return request<{ designs: DesignSummary[] }>('/designs');
}

export async function getDesign(designId: string): Promise<{
  design: DesignSummary;
  latest_version: DesignVersion;
  history: DesignVersion[];
}> {
  return request<{
    design: DesignSummary;
    latest_version: DesignVersion;
    history: DesignVersion[];
  }>(`/designs/${designId}`);
}

export async function createDesign(payload: CreateDesignPayload) {
  return request<any>('/designs', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateDesignParameters(designId: string, payload: ParameterUpdatePayload) {
  return request<any>(`/designs/${designId}/parameters`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function getDesignValidation(designId: string): Promise<{ design_id: string; validation: ValidationReport }> {
  return request<{ design_id: string; validation: ValidationReport }>(`/designs/${designId}/validation`);
}

export async function getDesignMaterials(designId: string): Promise<{ design_id: string; candidates: CandidateScore[] }> {
  return request<{ design_id: string; candidates: CandidateScore[] }>(`/designs/${designId}/materials`);
}
