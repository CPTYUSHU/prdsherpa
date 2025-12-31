import { useNavigate } from 'react-router-dom';
import { Button, Typography, Avatar, Space, Spin, Popconfirm, message, Divider } from 'antd';
import { PlusOutlined, UserOutlined, FileTextOutlined, DeleteOutlined, SettingOutlined } from '@ant-design/icons';
import { useApp } from '../../contexts/AppContext';
import { projectApi } from '../../services/api';
import AIModelSelector from '../AIModelSelector';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Text } = Typography;

const Sidebar = () => {
  const navigate = useNavigate();
  const { projects, currentProject, loading, setCurrentProject, refreshProjects } = useApp();

  const handleNewProject = () => {
    navigate('/project/new');
  };

  const handleSelectProject = (project: any) => {
    setCurrentProject(project);
    // 导航到需求列表页面
    navigate(`/project/${project.id}`);
  };

  const handleDeleteProject = async (projectId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡，避免触发选择项目
    try {
      await projectApi.delete(projectId);
      message.success('项目已删除');
      
      // 如果删除的是当前项目，清除当前项目并导航到首页
      if (currentProject?.id === projectId) {
        setCurrentProject(null);
        navigate('/');
      }
      
      // 刷新项目列表
      await refreshProjects();
    } catch (error: any) {
      console.error('Failed to delete project:', error);
      message.error('删除项目失败');
    }
  };

  return (
    <div className="sidebar">
      {/* 顶部 */}
      <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
        <Space style={{ width: '100%', flexDirection: 'column' }} size="middle">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
            <Text strong style={{ fontSize: '18px' }}>PRD助手</Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            block
            onClick={handleNewProject}
          >
            新建项目
          </Button>
        </Space>
      </div>

      {/* 项目列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin />
          </div>
        ) : projects.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: '#999' }}>
            <Text type="secondary">还没有项目</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              点击上方按钮创建第一个项目
            </Text>
          </div>
        ) : (
          <div>
            {(Array.isArray(projects) ? projects : []).map((project) => (
              <div
                key={project.id}
                style={{
                  padding: '12px',
                  cursor: 'pointer',
                  borderRadius: '8px',
                  background: currentProject?.id === project.id ? '#e6f7ff' : 'transparent',
                  border: currentProject?.id === project.id ? '1px solid #1890ff' : '1px solid transparent',
                  marginBottom: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
                onClick={() => handleSelectProject(project)}
              >
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <Text strong ellipsis style={{ fontSize: '14px', display: 'block' }}>
                    {project.name}
                  </Text>
                  <div style={{ marginTop: '4px' }}>
                    <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                      创建于 {dayjs(project.created_at).fromNow()}
                    </Text>
                    {project.last_conversation_at && (
                      <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                        最近对话 {dayjs(project.last_conversation_at).fromNow()}
                      </Text>
                    )}
                  </div>
                </div>
                <Popconfirm
                  title="删除项目"
                  description="确定要删除这个项目吗？此操作不可恢复。"
                  onConfirm={(e) => handleDeleteProject(project.id, e as any)}
                  onCancel={(e) => e?.stopPropagation()}
                  okText="删除"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={(e) => e.stopPropagation()}
                    style={{ flexShrink: 0, marginLeft: '8px' }}
                  />
                </Popconfirm>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 底部区域 */}
      <div style={{ borderTop: '1px solid #f0f0f0' }}>
        {/* AI 模型选择器 */}
        <div style={{ padding: '12px 16px' }}>
          <div style={{ marginBottom: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>AI 模型</Text>
          </div>
          <AIModelSelector size="small" style={{ width: '100%' }} />
        </div>

        <Divider style={{ margin: '0' }} />

        {/* API Key 设置 */}
        <div style={{ padding: '12px 16px' }}>
          <Button
            icon={<SettingOutlined />}
            onClick={() => navigate('/settings/api-keys')}
            block
            size="small"
          >
            API Key 设置
          </Button>
        </div>

        <Divider style={{ margin: '0' }} />

        {/* 用户信息 */}
        <div style={{ padding: '16px' }}>
          <Space>
            <Avatar icon={<UserOutlined />} />
            <Text>产品经理</Text>
          </Space>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

