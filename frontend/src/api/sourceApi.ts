import apiClient from './client';
import type { SourcePathRequest, SourceCheckResponse, ScanResult } from '../types/api';

export async function checkSourceDirectory(
  path: string
): Promise<SourceCheckResponse> {
  const response = await apiClient.post<SourceCheckResponse>(
    '/source/check',
    { path } as SourcePathRequest
  );
  return response.data;
}

export async function scanSourceDirectory(
  path: string
): Promise<ScanResult> {
  const response = await apiClient.post<ScanResult>('/source/scan', {
    path,
  } as SourcePathRequest);
  return response.data;
}
