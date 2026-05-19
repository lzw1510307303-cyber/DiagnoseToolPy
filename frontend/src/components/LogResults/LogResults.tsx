import { Card, List, Tag, Typography, Space, Pagination, Empty, Checkbox, Button, Collapse } from 'antd';
import { ClockCircleOutlined, DatabaseOutlined, CompressOutlined, ExpandOutlined } from '@ant-design/icons';
import { useState } from 'react';
import type { LogSearchResponse, LogRecord, CompressedLogGroup } from '../../types/logSearch';

const { Text } = Typography;

interface LogResultsProps {
  results: LogSearchResponse;
  keywords: string[];
  onPageChange: (page: number, pageSize: number) => void;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

function isCompressedGroup(item: LogRecord | CompressedLogGroup): item is CompressedLogGroup {
  return 'count' in item && 'first_log' in item;
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

function CompressedLogItem({
  group,
  keywords,
  isSelected,
  onToggle,
}: {
  group: CompressedLogGroup;
  keywords: string[];
  isSelected: boolean;
  onToggle: (ids: string[]) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const first = group.first_log;

  const handleCheckboxChange = (checked: boolean) => {
    if (checked) {
      onToggle([...group.log_ids]);
    } else {
      onToggle(group.log_ids.filter((id) => id !== group.log_ids[0]));
    }
  };

  return (
    <Card
      size="small"
      style={{
        marginBottom: 8,
        cursor: 'pointer',
        borderColor: isSelected ? '#1890ff' : undefined,
        backgroundColor: '#f0f0f0',
      }}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Space>
          <Checkbox
            checked={isSelected}
            onChange={(e) => handleCheckboxChange(e.target.checked)}
          />
          <Tag icon={<CompressOutlined />} color="purple">
            x{group.count}
          </Tag>
          <Tag color={getLevelColor(first.level)}>{first.level}</Tag>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <ClockCircleOutlined /> {first.timestamp}
          </Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <DatabaseOutlined /> {first.source}
          </Text>
          {first.thread_id && (
            <Tag>{first.thread_id}</Tag>
          )}
          <Button
            type="text"
            size="small"
            icon={<ExpandOutlined />}
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? '收起' : '展开'}
          </Button>
        </Space>

        <div style={{ fontFamily: 'monospace', wordBreak: 'break-all', paddingLeft: 24 }}>
          <HighlightText text={first.message} keywords={keywords} />
        </div>

        {expanded && (
          <div style={{ paddingLeft: 24 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              共 {group.count} 条相似日志:
            </Text>
            <ul style={{ margin: '8px 0', paddingLeft: 20 }}>
              {group.timestamps.map((ts, i) => (
                <li key={i} style={{ fontSize: 12, color: '#888' }}>
                  {ts} - {group.log_ids[i]}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Space>
    </Card>
  );
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
          {log.thread_id && <Tag>{log.thread_id}</Tag>}
        </Space>
        <div style={{ fontFamily: 'monospace', wordBreak: 'break-all', paddingLeft: 24 }}>
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

  const handleSelectionChange = (ids: string[]) => {
    onSelectionChange(ids);
  };

  const handleSelectAll = () => {
    const allIds = results.results.flatMap((item) =>
      isCompressedGroup(item) ? item.log_ids : [item.id]
    );
    if (selectedIds.length === allIds.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(allIds);
    }
  };

  if (!results || results.results.length === 0) {
    return (
      <Card style={{ marginTop: 16 }}>
        <Empty description="未找到匹配的日志" />
      </Card>
    );
  }

  const totalDisplay = results.compressed
    ? results.total_after_compress
    : results.total;

  const totalText = results.compressed
    ? `找到 ${results.total} 条原始日志，压缩后 ${totalDisplay} 组，当前显示 ${results.results.length} 组`
    : `找到 ${totalDisplay} 条日志，当前显示 ${results.results.length} 条`;

  return (
    <Card style={{ marginTop: 16 }}>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Space style={{ justifyContent: 'space-between', width: '100%' }}>
          <Text strong>{totalText}</Text>
          <Checkbox
            checked={
              results.results.length > 0 &&
              selectedIds.length ===
                results.results.flatMap((item) =>
                  isCompressedGroup(item) ? item.log_ids : [item.id]
                ).length
            }
            indeterminate={
              selectedIds.length > 0 &&
              selectedIds.length <
                results.results.flatMap((item) =>
                  isCompressedGroup(item) ? item.log_ids : [item.id]
                ).length
            }
            onChange={handleSelectAll}
          >
            全选
          </Checkbox>
        </Space>

        <List
          dataSource={results.results}
          renderItem={(item) =>
            isCompressedGroup(item) ? (
              <CompressedLogItem
                group={item}
                keywords={keywords}
                isSelected={item.log_ids.some((id) => selectedIds.includes(id))}
                onToggle={handleSelectionChange}
              />
            ) : (
              <LogItem
                log={item}
                keywords={keywords}
                isSelected={selectedIds.includes(item.id)}
                onToggle={handleToggle}
              />
            )
          }
        />

        <div style={{ textAlign: 'center' }}>
          <Pagination
            current={results.page}
            pageSize={results.page_size}
            total={totalDisplay}
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
