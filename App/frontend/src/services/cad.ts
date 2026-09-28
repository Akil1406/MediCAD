import { request } from './api';
import { CADProperties } from '../types';

export async function buildCadModel(spec: Record<string, any>): Promise<{
  success: boolean;
  device_type: string;
  cad_properties: CADProperties;
  stl_base64: string;
}> {
  return request<{
    success: boolean;
    device_type: string;
    cad_properties: CADProperties;
    stl_base64: string;
  }>('/cad/build', {
    method: 'POST',
    body: JSON.stringify(spec),
  });
}

export function getPreviewStlUrl(deviceType: string): string {
  return `/api/v1/cad/preview/${deviceType}`;
}
