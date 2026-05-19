import client from './client';

export interface LogDiagnosisRequest {
  logs: Array<{
    id: string;
    timestamp: string;
    level: string;
    source: string;
    message: string;
  }>;
  model?: string;
  system_prompt?: string;
}

export interface LogDiagnosisResponse {
  diagnosis: string;
  model_used: string;
  logs_analyzed: number;
}

export async function diagnoseLogs(request: LogDiagnosisRequest): Promise<LogDiagnosisResponse> {
  const response = await client.post<LogDiagnosisResponse>('/logs/diagnose', request);
  return response.data;
}
