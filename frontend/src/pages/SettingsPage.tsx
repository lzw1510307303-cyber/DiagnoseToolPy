import { Card, Descriptions, Empty } from 'antd';

function SettingsPage() {
  return (
    <div>
      <h1>Settings</h1>
      <Card title="Application Configuration" style={{ marginBottom: 24 }}>
        <Descriptions column={1}>
          <Descriptions.Item label="Application Name">DiagnoseToolPy</Descriptions.Item>
          <Descriptions.Item label="Version">0.1.0</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="Input Roots" style={{ marginBottom: 24 }}>
        <Empty description="No input roots configured. Update config/app.yaml to configure allowed input directories." />
      </Card>

      <Card title="Placeholder">
        <Empty description="Additional settings will be available in future updates." />
      </Card>
    </div>
  );
}

export default SettingsPage;
