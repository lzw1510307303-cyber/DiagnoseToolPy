// Compressed log group display card component

import { useState } from 'react';

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
import { Card, Badge, Button, Typography, Tag, Space, Divider } from 'antd';
import { CaretRightOutlined } from '@ant-design/icons';
import type { CompressedLogGroup, LogEntry } from '../../types/log';
import { expandLogGroup } from '../../api/logsApi';

const { Text, Paragraph } = Typography;

interface LogGroupCardProps {
  group: CompressedLogGroup;
}

function formatTimestamp(ts: string | null): string {
  if (!ts) return '-';
  return ts;
}

function getLevelColor(level: string | null): string {
  switch (level?.toUpperCase()) {
    case 'ERROR':
      return 'red';
    case 'WARN':
    case 'WARNING':
      return 'orange';
    case 'INFO':
      return 'blue';
    case 'DEBUG':
      return 'green';
    case 'TRACE':
      return 'purple';
    default:
      return 'default';
  }
}

function LogGroupCard({ group }: LogGroupCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [childLogs, setChildLogs] = useState<LogEntry[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = async () => {
    if (expanded) {
      setExpanded(false);
      return;
    }

    if (childLogs !== null) {
      setExpanded(true);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await expandLogGroup({ group_id: group.group_id });
      setChildLogs(response.logs);
      setExpanded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to expand group');
    } finally {
      setLoading(false);
    }
  };

  const renderLogLine = (log: LogEntry) => {
    const levelTag = log.level ? (
      <Tag color={getLevelColor(log.level)}>{log.level}</Tag>
    ) : null;

    const timestamp = log.timestamp ? (
      <Text type="secondary" style={{ fontSize: 12 }}>
        {log.timestamp}
      </Text>
    ) : null;

    const fileInfo = log.file_path && log.line_no ? (
      <Text type="secondary" style={{ fontSize: 12 }}>
        {log.file_path}:{log.line_no}
      </Text>
    ) : null;

    return (
      <div
        key={log.id}
        style={{
          paddingLeft: 16,
          paddingTop: 4,
          paddingBottom: 4,
          borderLeft: '2px solid #f0f0f0',
          marginLeft: 8,
        }}
      >
        <Space split={<Divider type="vertical" />}>
          {levelTag}
          {timestamp}
          {fileInfo}
        </Space>
        <Paragraph
          copyable={{ text: log.raw }}
          style={{ marginBottom: 4, marginTop: 4, fontFamily: 'monospace', fontSize: 12 }}
          ellipsis={{ rows: 2, expandable: true, symbol: 'more' }}
        >
          {escapeHtml(log.raw)}
        </Paragraph>
      </div>
    );
  };

  return (
    <Card
      size="small"
      style={{ marginBottom: 8 }}
      bodyStyle={{ padding: 12 }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
        <CaretRightOutlined
          style={{
            marginTop: 4,
            transition: 'transform 0.2s',
            transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
          }}
        />
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Header row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Tag color={getLevelColor(group.level)}>{group.level || 'UNKNOWN'}</Tag>
            <Text strong style={{ fontFamily: 'monospace' }}>
              {escapeHtml(group.first_log.raw.slice(0, 100))}
              {group.first_log.raw.length > 100 ? '...' : ''}
            </Text>
          </div>

          {/* Stats row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 8 }}>
            <Badge count={`×${group.count}`} style={{ backgroundColor: '#1890ff' }} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              First: {formatTimestamp(group.timestamps.first)}
            </Text>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Last: {formatTimestamp(group.timestamps.last)}
            </Text>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Type: {group.group_type}
            </Text>
          </div>

          {/* Expand/Collapse button */}
          <Button
            type="link"
            size="small"
            loading={loading}
            onClick={handleToggle}
            style={{ padding: 0 }}
          >
            {expanded ? '收起 (Collapse)' : `展开查看 ${group.count} 条日志 (Expand ${group.count} logs)`}
          </Button>

          {/* Error message */}
          {error && (
            <Text type="danger" style={{ display: 'block', marginTop: 4, fontSize: 12 }}>
              {error}
            </Text>
          )}

          {/* Expanded child logs */}
          {expanded && childLogs && (
            <div style={{ marginTop: 8 }}>
              <Divider style={{ margin: '8px 0' }} />
              {childLogs.map(renderLogLine)}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

export default LogGroupCard;
