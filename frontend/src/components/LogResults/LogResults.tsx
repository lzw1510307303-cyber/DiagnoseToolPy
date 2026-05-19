import { Card, List, Tag, Typography, Space, Pagination, Empty, Checkbox } from 'antd';
import { ClockCircleOutlined, DatabaseOutlined } from '@ant-design/icons';
import type { LogSearchResponse, LogRecord } from '../../types/logSearch';

const { Text } = Typography;

interface LogResultsProps {
  results: LogSearchResponse;
  keywords: string[];
  onPageChange: (page: number, pageSize: number) => void;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

function HighlightText({ text, keywords }: { text: string; keywords: string[] }) {
  if (!keywords || keywords.length === 0) {
    return <span>{text}</span>;
  }

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

function LogItem({
  log,
  keywords,
  isSelected,
  onToggle,
}: {
  log: LogRecord;
  keywords: string[];
  isSelected: boolean;
  onToggle: (id: string) => void;
}) {
  return (
    <Card
      size="small"
      style={{
        marginBottom: 8,
        cursor: 'pointer',
        borderColor: isSelected ? '#1890ff' : undefined,
      }}
      onClick={() => onToggle(log.id)}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Space>
          <Checkbox checked={isSelected} onChange={() => onToggle(log.id)} />
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

export default function LogResults({
  results,
  keywords,
  onPageChange,
  selectedIds,
  onSelectionChange,
}: LogResultsProps) {
  const handleToggle = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((i) => i !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === results.results.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(results.results.map((r) => r.id));
    }
  };

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
        <Space style={{ justifyContent: 'space-between', width: '100%' }}>
          <Text strong>
            找到 {results.total} 条匹配的日志，已选择 {selectedIds.length} 条
          </Text>
          <Checkbox
            checked={selectedIds.length === results.results.length && results.results.length > 0}
            indeterminate={
              selectedIds.length > 0 && selectedIds.length < results.results.length
            }
            onChange={handleSelectAll}
          >
            全选当前页
          </Checkbox>
        </Space>

        <List
          dataSource={results.results}
          renderItem={(item) => (
            <LogItem
              log={item}
              keywords={keywords}
              isSelected={selectedIds.includes(item.id)}
              onToggle={handleToggle}
            />
          )}
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
