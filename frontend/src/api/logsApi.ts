// Log search and compression API wrapper

import apiClient from './client';
import type {
  LogSearchRequest,
  LogSearchResponse,
  LogExpandRequest,
  LogExpandResponse,
} from '../types/log';

export async function searchLogs(
  request: LogSearchRequest
): Promise<LogSearchResponse> {
  const response = await apiClient.post<LogSearchRequest, LogSearchResponse>(
    '/logs/search',
    request
  );
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (response as any).data as LogSearchResponse;
}

export async function expandLogGroup(
  request: LogExpandRequest
): Promise<LogExpandResponse> {
  const response = await apiClient.post<LogExpandRequest, LogExpandResponse>(
    '/logs/expand',
    request
  );
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (response as any).data as LogExpandResponse;
}
