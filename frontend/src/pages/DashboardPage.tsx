import { Card, Row, Col } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  FileSearchOutlined,
  FolderOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { Meta } = Card;

const cardData = [
  {
    title: 'Analysis Tasks',
    description: 'Scan server directories and analyze log files',
    icon: <FileSearchOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
    path: '/analysis',
  },
  {
    title: 'Casebase',
    description: 'Browse and manage fault cases',
    icon: <FolderOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
    path: '/cases',
  },
  {
    title: 'Settings',
    description: 'Configure input roots and application settings',
    icon: <SettingOutlined style={{ fontSize: 48, color: '#faad14' }} />,
    path: '/settings',
  },
];

function DashboardPage() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Dashboard</h1>
      <Row gutter={[16, 16]}>
        {cardData.map((card) => (
          <Col xs={24} sm={12} md={8} key={card.path}>
            <Card
              hoverable
              onClick={() => navigate(card.path)}
              style={{ textAlign: 'center' }}
            >
              <div style={{ marginBottom: 16 }}>{card.icon}</div>
              <Meta title={card.title} description={card.description} />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default DashboardPage;
