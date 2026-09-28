const API_BASE = '/api/v1';

export class ApiError extends Error {
  code?: string;
  field?: string;
  constructor(message: string, code?: string, field?: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.field = field;
  }
}

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      let errData: any = {};
      try {
        errData = await response.json();
      } catch {
        // Not JSON
      }
      
      const detail = errData.detail || errData.error || {};
      const message = typeof detail === 'string' ? detail : (detail.message || `Request failed with status ${response.status}`);
      const code = typeof detail === 'object' ? detail.code : undefined;
      const field = typeof detail === 'object' ? detail.field : undefined;
      
      throw new ApiError(message, code, field);
    }

    return await response.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err.message || 'Network error occurred');
  }
}
