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

export type MatchMode = 'AND' | 'OR';

export interface SearchState {
  keywords: string;
  matchMode: MatchMode;
  excludeKeywords: string;
  logLevels: string[];
  startTime: string | null;
  endTime: string | null;
  page: number;
  pageSize: number;
}
