import type { HealthResponse } from '../types/api';

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health');
  return response.json();
}

export function listCases(): Promise<unknown[]> {
  return Promise.resolve([]);
}

export function getCase(_caseId: string): Promise<unknown> {
  return Promise.resolve(null);
}
