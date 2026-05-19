// Log types for the log search and compression feature

export type CompressType = 'message' | 'thread_id' | 'both' | 'none';

export interface LogEntry {
  id: string;
  timestamp: string | null;
  level: string | null;
  module: string | null;
  thread: string | null;
  logger: string | null;
  message: string | null;
  raw: string;
  file_path: string | null;
  line_no: number | null;
}

export interface CompressedLogGroup {
  group_id: string;
  group_type: 'thread_id' | 'message' | 'both';
  key_value: string;
  count: number;
  first_log: LogEntry;
  last_log: LogEntry;
  timestamps: { first: string; last: string };
  log_ids: string[];
  level: string;
}

export interface LogSearchRequest {
  query: string;
  compress?: CompressType;
  file_paths?: string[];
  level_filter?: string[];
  time_range?: { start?: string; end?: string };
  max_results?: number;
}

export interface LogSearchResponse {
  total_count: number;
  compressed_count: number;
  compress_type: string;
  results: (LogEntry | CompressedLogGroup)[];
  search_time_ms: number;
}

export interface LogExpandRequest {
  group_id: string;
}

export interface LogExpandResponse {
  group_id: string;
  logs: LogEntry[];
}

export type LogResult = LogEntry | CompressedLogGroup;

export function isCompressedLogGroup(item: LogResult): item is CompressedLogGroup {
  return 'group_id' in item && 'group_type' in item && 'count' in item;
}
