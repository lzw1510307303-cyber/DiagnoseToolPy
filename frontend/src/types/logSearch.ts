export interface LogSearchRequest {
  keywords: string[];
  match_mode: 'AND' | 'OR';
  exclude_keywords?: string[];
  log_levels?: string[];
  start_time?: string;
  end_time?: string;
  page?: number;
  page_size?: number;
  compress?: boolean;
  compress_by?: 'message' | 'thread_id' | 'both';
}

export interface LogRecord {
  id: string;
  timestamp: string;
  level: string;
  source: string;
  message: string;
  thread_id?: string;
  highlights?: Record<string, string[]>;
}

export interface CompressedLogGroup {
  count: number;
  first_log: LogRecord;
  timestamps: string[];
  log_ids: string[];
}

export interface LogSearchResponse {
  total: number;
  total_after_compress?: number;
  page: number;
  page_size: number;
  results: (LogRecord | CompressedLogGroup)[];
  compressed: boolean;
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
  compress: boolean;
  compressBy: 'message' | 'thread_id' | 'both';
}
