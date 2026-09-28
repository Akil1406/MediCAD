import { request } from './api';

export interface AgentResponse {
  status: string;
  target_device_type: string;
  specification: Record<string, any>;
  cad_result: Record<string, any>;
  geometry_checks: Record<string, any>;
  material_candidates: Record<string, any>[];
  engineering_report: string;
}

export async function runAiAgent(prompt: string): Promise<AgentResponse> {
  return request<AgentResponse>('/ai/agent', {
    method: 'POST',
    body: JSON.stringify({ prompt }),
  });
}
