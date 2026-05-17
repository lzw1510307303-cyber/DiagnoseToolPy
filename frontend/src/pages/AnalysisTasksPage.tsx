import { useState } from 'react';
import { Input, Button, Result, Spin, Alert, Card, Statistic, Row, Col } from 'antd';
import { FileSearchOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { checkSourceDirectory, scanSourceDirectory } from '../api/sourceApi';
import type { SourceCheckResponse, ScanResult } from '../types/api';

function AnalysisTasksPage() {
  const [path, setPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkResult, setCheckResult] = useState<SourceCheckResponse | null>(null);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheck = async () => {
    if (!path.trim()) return;
    setLoading(true);
    setError(null);
    setCheckResult(null);
    setScanResult(null);

    try {
      const result = await checkSourceDirectory(path);
      setCheckResult(result);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to check directory');
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async () => {
    if (!path.trim()) return;
    setLoading(true);
    setError(null);
    setScanResult(null);

    try {
      const result = await scanSourceDirectory(path);
      setScanResult(result);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to scan directory');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Analysis Tasks</h1>
      <Card style={{ marginBottom: 24 }}>
        <Input
          size="large"
          placeholder="Enter directory path (e.g., /data/diagnose/input)"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          style={{ marginBottom: 16 }}
        />
        <div style={{ display: 'flex', gap: 8 }}>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={handleCheck}
            loading={loading}
          >
            Check Directory
          </Button>
          <Button
            icon={<FileSearchOutlined />}
            onClick={handleScan}
            loading={loading}
            disabled={!path.trim()}
          >
            Scan Directory
          </Button>
        </div>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', margin: 24 }}>
          <Spin size="large" tip="Processing..." />
        </div>
      )}

      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {checkResult && !scanResult && (
        <Result
          status={checkResult.allowed ? 'success' : 'error'}
          icon={checkResult.allowed ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          title={checkResult.allowed ? 'Directory is allowed' : 'Directory is not allowed'}
          subTitle={`Path: ${checkResult.path}`}
        />
      )}

      {scanResult && (
        <Card title="Scan Results">
          <Row gutter={[16, 16]}>
            <Col xs={12} sm={6}>
              <Statistic title="Total Files" value={scanResult.total_files} />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic
                title="Total Size"
                value={scanResult.total_bytes}
                formatter={(value) => `${(Number(value) / 1024 / 1024).toFixed(2)} MB`}
              />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic title="Error Count" value={scanResult.error_count} valueStyle={{ color: '#cf1322' }} />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic title="Warning Count" value={scanResult.warn_count} valueStyle={{ color: '#faad14' }} />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
}

export default AnalysisTasksPage;
