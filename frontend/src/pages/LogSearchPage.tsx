// Log search page with compression support

import { useState } from 'react';
import {
  Card,
  Input,
  Button,
  Typography,
  Spin,
  Alert,
  Space,
  Divider,
  Tag,
  Empty,
} from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import CompressionControl from '../components/logs/CompressionControl';
import LogGroupCard from '../components/logs/LogGroupCard';
import { searchLogs } from '../api/logsApi';
import type {
  CompressType,
  LogSearchResponse,
  LogResult,
  LogEntry,
} from '../types/log';
import { isCompressedLogGroup } from '../types/log';

const { Title, Text, Paragraph } = Typography;

/**
 * Escape HTML special characters to prevent XSS attacks.
 * Use this when rendering user-controlled content in the DOM.
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };
  return text.replace(/[&<>"']/g, (char) => map[char]);
}
const { Search } = Input;

function LogSearchPage() {
  const [query, setQuery] = useState('');
  const [compressType, setCompressType] = useState<CompressType>('none');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<LogSearchResponse | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await searchLogs({
        query: query.trim(),
        compress: compressType,
        max_results: 1000,
      });
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResponse(null);
    setError(null);
  };

  const renderPlainLog = (log: LogEntry) => {
    const levelColor =
      log.level === 'ERROR'
        ? 'red'
        : log.level === 'WARN'
        ? 'orange'
        : log.level === 'INFO'
        ? 'blue'
        : 'default';

    return (
      <Card
        key={log.id}
        size="small"
        style={{ marginBottom: 4 }}
        bodyStyle={{ padding: '8px 12px' }}
      >
        <Space split={<Divider type="vertical" />}>
          {log.level && <Tag color={levelColor}>{log.level}</Tag>}
          {log.timestamp && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {log.timestamp}
            </Text>
          )}
          {log.file_path && log.line_no && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {log.file_path}:{log.line_no}
            </Text>
          )}
        </Space>
        <Paragraph
          copyable={{ text: log.raw }}
          style={{
            marginBottom: 0,
            marginTop: 4,
            fontFamily: 'monospace',
            fontSize: 12,
          }}
          ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}
        >
          {escapeHtml(log.raw)}
        </Paragraph>
      </Card>
    );
  };

  const renderResultItem = (item: LogResult) => {
    if (isCompressedLogGroup(item)) {
      return <LogGroupCard key={item.group_id} group={item} />;
    }
    return renderPlainLog(item);
  };

  return (
    <div>
      <Title level={2}>Log Search</Title>

      {/* Search controls */}
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Space.Compact style={{ width: '100%' }}>
            <Search
              placeholder="Enter search keywords (e.g., timeout, error, exception)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onSearch={handleSearch}
              onPressEnter={handleSearch}
              enterButton={
                <Button type="primary" icon={<SearchOutlined />}>
                  Search
                </Button>
              }
              size="large"
              allowClear
              onClear={handleClear}
            />
          </Space.Compact>

          <Space align="center">
            <Text type="secondary">Compression:</Text>
            <CompressionControl value={compressType} onChange={setCompressType} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              (none=show all, message=dedupe by content, thread_id=group by thread, both=nested)
            </Text>
          </Space>
        </Space>
      </Card>

      {/* Loading state */}
      {loading && (
        <div style={{ textAlign: 'center', margin: 48 }}>
          <Spin size="large" tip="Searching logs..." />
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <Alert
          message="Search Failed"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Results */}
      {!loading && response && (
        <div>
          {/* Stats header */}
          <Card size="small" style={{ marginBottom: 16 }} bodyStyle={{ padding: '8px 12px' }}>
            <Space split={<Divider type="vertical" />}>
              <Text>
                Total: <strong>{response.total_count}</strong> logs
              </Text>
              <Text>
                Displayed: <strong>{response.compressed_count}</strong>{' '}
                {response.compress_type !== 'none' ? 'groups' : 'logs'}
              </Text>
              <Text type="secondary">Search time: {response.search_time_ms}ms</Text>
              <Text type="secondary">Compression: {response.compress_type}</Text>
            </Space>
          </Card>

          {/* Results list */}
          {response.results.length === 0 ? (
            <Empty description="No matching logs found" />
          ) : (
            <div>{response.results.map(renderResultItem)}</div>
          )}
        </div>
      )}
    </div>
  );
}

export default LogSearchPage;
