import { useNavigate } from 'react-router-dom';
import { Button, Typography, Space } from 'antd';
import { PlusOutlined, FileTextOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Welcome = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#fafafa',
    }}>
      <Space style={{ flexDirection: 'column' }} align="center" size="large">
        <FileTextOutlined style={{ fontSize: '80px', color: '#1890ff' }} />
        <Title level={2}>欢迎使用 PRD助手</Title>
        <Paragraph style={{ textAlign: 'center', color: '#666', maxWidth: '500px' }}>
          AI 驱动的产品需求文档写作助手<br />
          通过对话式交互，帮助你快速撰写专业的 PRD 文档
        </Paragraph>
        <Button
          type="primary"
          size="large"
          icon={<PlusOutlined />}
          onClick={() => navigate('/project/new')}
        >
          创建第一个项目
        </Button>
      </Space>
    </div>
  );
};

export default Welcome;

