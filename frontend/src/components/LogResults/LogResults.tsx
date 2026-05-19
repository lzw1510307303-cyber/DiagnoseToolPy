import { Card, List, Tag, Typography, Space, Pagination, Empty } from 'antd';
import { ClockCircleOutlined, DatabaseOutlined } from '@ant-design/icons';
import type { LogSearchResponse, LogRecord } from '../../types/logSearch';

const { Text } = Typography;

interface LogResultsProps {
  results: LogSearchResponse;
  keywords: string[];
  onPageChange: (page: number, pageSize: number) => void;
}

function HighlightText({ text, keywords }: { text: string; keywords: string[] }) {
  if (!keywords || keywords.length === 0) {
    return <span>{text}</span>;
  }

  // Simple highlight - replace keywords with styled spans
  let result = text;
  keywords.forEach((keyword) => {
    if (keyword.trim()) {
      const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      result = result.replace(regex, '<mark class="highlight">$1</mark>');
    }
  });

  return <span dangerouslySetInnerHTML={{ __html: result }} />;
}

function getLevelColor(level: string): string {
  switch (level.toUpperCase()) {
    case 'ERROR':
      return 'red';
    case 'WARNING':
      return 'orange';
    case 'INFO':
      return 'blue';
    case 'DEBUG':
      return 'gray';
    default:
      return 'default';
  }
}

function LogItem({ log, keywords }: { log: LogRecord; keywords: string[] }) {
  return (
    <Card size="small" style={{ marginBottom: 8 }}>
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Space>
          <Tag color={getLevelColor(log.level)}>{log.level}</Tag>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <ClockCircleOutlined /> {log.timestamp}
          </Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <DatabaseOutlined /> {log.source}
          </Text>
        </Space>
        <div style={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
          <HighlightText text={log.message} keywords={keywords} />
        </div>
      </Space>
    </Card>
  );
}

export default function LogResults({ results, keywords, onPageChange }: LogResultsProps) {
  if (!results || results.total === 0) {
    return (
      <Card style={{ marginTop: 16 }}>
        <Empty description="未找到匹配的日志" />
      </Card>
    );
  }

  return (
    <Card style={{ marginTop: 16 }}>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Text strong>
          找到 {results.total} 条匹配的日志，当前显示 {(results.page - 1) * results.page_size + 1}-
          {Math.min(results.page * results.page_size, results.total)} 条
        </Text>

        <List
          dataSource={results.results}
          renderItem={(item) => <LogItem log={item} keywords={keywords} />}
        />

        <div style={{ textAlign: 'center' }}>
          <Pagination
            current={results.page}
            pageSize={results.page_size}
            total={results.total}
            onChange={onPageChange}
            showSizeChanger
            showQuickJumper
            showTotal={(total) => `共 ${total} 条`}
          />
        </div>
      </Space>
    </Card>
  );
}
