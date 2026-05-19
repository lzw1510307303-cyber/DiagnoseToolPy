import client from './client';

export interface LogSearchRequest {
  keywords: string[];
  match_mode: 'AND' | 'OR';
  exclude_keywords?: string[];
  log_levels?: string[];
  start_time?: string;
  end_time?: string;
  page?: number;
  page_size?: number;
}

export interface LogRecord {
  id: string;
  timestamp: string;
  level: string;
  source: string;
  message: string;
  highlights?: Record<string, string[]>;
}

export interface LogSearchResponse {
  total: number;
  page: number;
  page_size: number;
  results: LogRecord[];
}

export interface ErrorResponse {
  error_code: string;
  message: string;
}

export async function searchLogs(request: LogSearchRequest): Promise<LogSearchResponse> {
  const response = await client.post<LogSearchResponse>('/logs/search', request);
  return response.data;
}

export async function getKeywordHistory(): Promise<{ history: string[] }> {
  const response = await client.get<{ history: string[] }>('/logs/history');
  return response.data;
}

export async function exportLogs(
  format: 'json' | 'csv' | 'txt',
  keywords: string,
  matchMode: 'AND' | 'OR'
): Promise<{ format: string; message: string; data: unknown[] }> {
  const response = await client.get('/logs/export', {
    params: {
      format,
      keywords,
      match_mode: matchMode,
    },
  });
  return response.data;
}
