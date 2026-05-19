import { useState } from 'react';
import {
  Input,
  Select,
  Button,
  Space,
  Card,
  Typography,
  DatePicker,
  Tag,
  Tooltip,
  message,
  Modal,
  Alert,
  Spin,
  Descriptions,
  Switch,
  Divider,
} from 'antd';
import { QuestionCircleOutlined, SearchOutlined, ClearOutlined, RobotOutlined, CompressOutlined } from '@ant-design/icons';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import type { MatchMode, SearchState } from '../../types/logSearch';
import { searchLogs } from '../../api/logSearchApi';
import type { LogSearchResponse } from '../../types/logSearch';
import { diagnoseLogs } from '../../api/logDiagnosisApi';
import LogResults from '../LogResults/LogResults';

const { Text } = Typography;
const { RangePicker } = DatePicker;

interface LogSearchPanelProps {
  onResults?: (results: LogSearchResponse) => void;
}

export default function LogSearchPanel({ onResults }: LogSearchPanelProps) {
  const [loading, setLoading] = useState(false);
  const [searchState, setSearchState] = useState<SearchState>({
    keywords: '',
    matchMode: 'AND',
    excludeKeywords: '',
    logLevels: [],
    startTime: null,
    endTime: null,
    page: 1,
    pageSize: 20,
    compress: false,
    compressBy: 'message',
  });
  const [results, setResults] = useState<LogSearchResponse | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectedLogs, setSelectedLogs] = useState<LogSearchResponse['results']>([]);

  // Diagnosis modal state
  const [diagVisible, setDiagVisible] = useState(false);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagModel, setDiagModel] = useState<string>('MiniMax-M2.7-32K');
  const [diagResult, setDiagResult] = useState<string | null>(null);
  const [diagError, setDiagError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!searchState.keywords.trim()) {
      message.warning('请输入关键词');
      return;
    }

    const keywords = searchState.keywords
      .split(/[,，]/)
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    if (keywords.length === 0) {
      message.warning('请输入有效的关键词');
      return;
    }

    if (keywords.length > 20) {
      message.warning('最多支持20个关键词');
      return;
    }

    const excludeKeywords = searchState.excludeKeywords
      .split(/[,，]/)
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    if (excludeKeywords.length > 5) {
      message.warning('最多支持5个排除关键词');
      return;
    }

    setLoading(true);
    try {
      const response = await searchLogs({
        keywords,
        match_mode: searchState.matchMode,
        exclude_keywords: excludeKeywords.length > 0 ? excludeKeywords : undefined,
        log_levels: searchState.logLevels.length > 0 ? searchState.logLevels : undefined,
        start_time: searchState.startTime || undefined,
        end_time: searchState.endTime || undefined,
        page: searchState.page,
        page_size: searchState.pageSize,
        compress: searchState.compress,
        compress_by: searchState.compressBy,
      });
      setResults(response);
      setSelectedIds([]);
      onResults?.(response);
    } catch (error) {
      console.error('Search failed:', error);
      message.error('搜索失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSearchState({
      keywords: '',
      matchMode: 'AND',
      excludeKeywords: '',
      logLevels: [],
      startTime: null,
      endTime: null,
      page: 1,
      pageSize: 20,
      compress: false,
      compressBy: 'message',
    });
    setResults(null);
    setSelectedIds([]);
  };

  const handlePageChange = (page: number, pageSize: number) => {
    setSearchState((prev) => ({ ...prev, page, pageSize }));
    setSelectedIds([]);
    setTimeout(handleSearch, 0);
  };

  const handleTimeRangeChange = (dates: [Dayjs | null, Dayjs | null] | null) => {
    if (dates && dates[0] && dates[1]) {
      setSearchState((prev) => ({
        ...prev,
        startTime: dates[0]!.toISOString(),
        endTime: dates[1]!.toISOString(),
      }));
    } else {
      setSearchState((prev) => ({
        ...prev,
        startTime: null,
        endTime: null,
      }));
    }
  };

  const handleSelectionChange = (ids: string[]) => {
    setSelectedIds(ids);
    if (results) {
      const allItems = results.results;
      const selected = allItems.filter((r) => {
        if ('count' in r && 'first_log' in r) {
          // Compressed group - check if any log ID in the group is selected
          return r.log_ids.some((id: string) => ids.includes(id));
        }
        return ids.includes(r.id);
      });
      setSelectedLogs(selected);
    }
  };

  const handleDiagnose = () => {
    if (selectedIds.length === 0) {
      message.warning('请先选择要诊断的日志');
      return;
    }
    setDiagVisible(true);
    setDiagResult(null);
    setDiagError(null);
  };

  const handleDiagSubmit = async () => {
    if (selectedLogs.length === 0) {
      message.warning('没有选中的日志');
      return;
    }

    setDiagLoading(true);
    setDiagError(null);
    setDiagResult(null);

    try {
      const logsToSend = selectedLogs.map((log) => {
        if ('first_log' in log) {
          return {
            id: log.first_log.id,
            timestamp: log.first_log.timestamp,
            level: log.first_log.level,
            source: log.first_log.source,
            message: log.first_log.message,
          };
        }
        return {
          id: log.id,
          timestamp: log.timestamp,
          level: log.level,
          source: log.source,
          message: log.message,
        };
      });

      const response = await diagnoseLogs({
        logs: logsToSend,
        model: diagModel,
      });
      setDiagResult(response.diagnosis);
    } catch (error) {
      console.error('Diagnosis failed:', error);
      setDiagError(error instanceof Error ? error.message : '诊断失败，请重试');
    } finally {
      setDiagLoading(false);
    }
  };

  return (
    <Card title="日志检索 - 多关键词搜索" style={{ width: '100%' }}>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 关键词输入 */}
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Text strong>关键词（多个用逗号分隔，最多20个）</Text>
          <Input.TextArea
            placeholder="请输入关键词，例如：error,database timeout"
            value={searchState.keywords}
            onChange={(e) =>
              setSearchState((prev) => ({ ...prev, keywords: e.target.value }))
            }
            rows={2}
            maxLength={1000}
          />
        </Space>

        {/* 匹配模式 */}
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Space align="center">
            <Text strong>匹配模式</Text>
            <Tooltip title="AND: 所有关键词都必须匹配 OR: 任一关键词匹配即可">
              <QuestionCircleOutlined />
            </Tooltip>
          </Space>
          <Select
            value={searchState.matchMode}
            onChange={(value) =>
              setSearchState((prev) => ({ ...prev, matchMode: value }))
            }
            style={{ width: 200 }}
            options={[
              { value: 'AND', label: 'AND（同时匹配）' },
              { value: 'OR', label: 'OR（任一匹配）' },
            ]}
          />
        </Space>

        {/* 排除关键词 */}
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Space align="center">
            <Text strong>排除关键词（最多5个）</Text>
            <Tooltip title="排除包含这些关键词的日志">
              <QuestionCircleOutlined />
            </Tooltip>
          </Space>
          <Input
            placeholder="请输入要排除的关键词，多个用逗号分隔"
            value={searchState.excludeKeywords}
            onChange={(e) =>
              setSearchState((prev) => ({
                ...prev,
                excludeKeywords: e.target.value,
              }))
            }
          />
        </Space>

        {/* 日志级别和时间范围 */}
        <Space wrap>
          <Space direction="vertical" size="small">
            <Text strong>日志级别</Text>
            <Select
              mode="multiple"
              placeholder="选择日志级别"
              value={searchState.logLevels}
              onChange={(value) =>
                setSearchState((prev) => ({ ...prev, logLevels: value }))
              }
              style={{ minWidth: 200 }}
              options={[
                { value: 'ERROR', label: <Tag color="red">ERROR</Tag> },
                { value: 'WARNING', label: <Tag color="orange">WARNING</Tag> },
                { value: 'INFO', label: <Tag color="blue">INFO</Tag> },
                { value: 'DEBUG', label: <Tag color="gray">DEBUG</Tag> },
              ]}
            />
          </Space>

          <Space direction="vertical" size="small">
            <Space>
              <Text strong>日志压缩</Text>
              <Tooltip title="开启后将相同消息或线程的日志合并显示，减少重复信息">
                <QuestionCircleOutlined />
              </Tooltip>
              <Switch
                size="small"
                checked={searchState.compress}
                onChange={(checked) =>
                  setSearchState((prev) => ({ ...prev, compress: checked }))
                }
              />
            </Space>
            {searchState.compress && (
              <Select
                value={searchState.compressBy}
                onChange={(value) =>
                  setSearchState((prev) => ({ ...prev, compressBy: value }))
                }
                style={{ width: 150 }}
                options={[
                  { value: 'message', label: '按消息内容' },
                  { value: 'thread_id', label: '按线程ID' },
                  { value: 'both', label: '消息+线程' },
                ]}
              />
            )}
          </Space>

          <Space direction="vertical" size="small">
            <Text strong>时间范围（默认24小时）</Text>
            <RangePicker
              showTime
              value={[
                searchState.startTime ? dayjs(searchState.startTime) : null,
                searchState.endTime ? dayjs(searchState.endTime) : null,
              ]}
              onChange={handleTimeRangeChange}
            />
          </Space>
        </Space>

        {/* 操作按钮 */}
        <Space>
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
          >
            搜索
          </Button>
          <Button icon={<ClearOutlined />} onClick={handleReset}>
            重置
          </Button>
          {results && results.total > 0 && (
            <Button
              type="default"
              icon={<RobotOutlined />}
              onClick={handleDiagnose}
              disabled={selectedIds.length === 0}
            >
              {selectedIds.length > 0
                ? `诊断已选日志 (${selectedIds.length})`
                : '选择日志后诊断'}
            </Button>
          )}
        </Space>
      </Space>

      {/* 搜索结果 */}
      {results && (
        <LogResults
          results={results}
          keywords={searchState.keywords.split(/[,，]/).filter((k) => k.trim())}
          onPageChange={handlePageChange}
          selectedIds={selectedIds}
          onSelectionChange={handleSelectionChange}
        />
      )}

      {/* 诊断 Modal */}
      <Modal
        title="AI 日志诊断"
        open={diagVisible}
        onCancel={() => setDiagVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setDiagVisible(false)}>
            关闭
          </Button>,
          <Button
            key="submit"
            type="primary"
            loading={diagLoading}
            onClick={handleDiagSubmit}
            disabled={selectedLogs.length === 0}
          >
            开始诊断
          </Button>,
        ]}
        width={700}
      >
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Descriptions column={2} size="small" bordered>
            <Descriptions.Item label="已选日志数量">
              {selectedLogs.length} 条
            </Descriptions.Item>
            <Descriptions.Item label="选择的大模型">
              <Select
                value={diagModel}
                onChange={setDiagModel}
                style={{ width: 200 }}
                options={[
                  { value: 'MiniMax-M2.7-32K', label: 'MiniMax M2.7-32K' },
                  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
                  { value: 'gpt-4o', label: 'GPT-4o' },
                  { value: 'claude-3-haiku', label: 'Claude 3 Haiku' },
                ]}
              />
            </Descriptions.Item>
          </Descriptions>

          {diagError && (
            <Alert
              message="诊断失败"
              description={diagError}
              type="error"
              showIcon
            />
          )}

          {diagResult && (
            <Alert
              message="AI 诊断结果"
              description={
                <pre
                  style={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    fontFamily: 'inherit',
                    maxHeight: 400,
                    overflow: 'auto',
                  }}
                >
                  {diagResult}
                </pre>
              }
              type="info"
              showIcon
            />
          )}

          {diagLoading && (
            <div style={{ textAlign: 'center', padding: 24 }}>
              <Spin size="large" tip="正在分析日志..." />
            </div>
          )}

          {!diagResult && !diagLoading && (
            <Alert
              message="注意事项"
              description='点击"开始诊断"后，AI 将分析您选择的日志条目并给出可能的故障原因和建议。'
              type="warning"
              showIcon
            />
          )}
        </Space>
      </Modal>
    </Card>
  );
}
