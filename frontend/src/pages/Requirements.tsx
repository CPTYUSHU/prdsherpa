import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Button,
  Card,
  Empty,
  Space,
  Typography,
  Spin,
  message,
  Modal,
  Input,
  Tag,
  Popconfirm,
  Tooltip,
  Badge,
} from 'antd';
import {
  PlusOutlined,
  MessageOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  FileTextOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { conversationApi } from '../services/api';
import type { Conversation } from '../types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Title, Text, Paragraph } = Typography;

const Requirements = () => {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);
  const [newReqModalVisible, setNewReqModalVisible] = useState(false);
  const [newReqName, setNewReqName] = useState('');
  const [creating, setCreating] = useState(false);
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  useEffect(() => {
    if (projectId) {
      loadConversations();
    }
  }, [projectId]);

  const loadConversations = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const data = await conversationApi.listByProject(projectId);
      setConversations(data || []);
    } catch (error: any) {
      console.error('Failed to load requirements:', error);
      message.error('加载需求列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequirement = async () => {
    if (!projectId || !newReqName.trim()) {
      message.warning('请输入需求名称');
      return;
    }

    try {
      setCreating(true);
      const newConv = await conversationApi.create(projectId, newReqName.trim());
      message.success('需求创建成功！');
      setNewReqModalVisible(false);
      setNewReqName('');

      // 刷新列表
      await loadConversations();

      // 跳转到聊天页面
      navigate(`/project/${projectId}/requirement/${newConv.id}`);
    } catch (error: any) {
      console.error('Failed to create requirement:', error);
      message.error('创建需求失败');
    } finally {
      setCreating(false);
    }
  };

  const handleMarkAsCompleted = async (convId: string) => {
    try {
      await conversationApi.updateStatus(convId, 'completed', true);
      message.success({
        content: (
          <div>
            <div>✅ 需求已标记为完成！</div>
            <div style={{ fontSize: '12px', marginTop: '4px' }}>
              AI 已生成需求摘要并归档到知识库，
              <a onClick={() => navigate(`/project/${projectId}/knowledge`)} style={{ marginLeft: '4px' }}>
                点击查看知识库
              </a>
            </div>
          </div>
        ),
        duration: 5,
      });

      // 刷新列表
      await loadConversations();
    } catch (error: any) {
      console.error('Failed to mark as completed:', error);
      message.error('标记失败');
    }
  };

  const handleDeleteRequirement = async (convId: string) => {
    try {
      await conversationApi.delete(convId);
      message.success('需求已删除');
      await loadConversations();
    } catch (error: any) {
      console.error('Failed to delete requirement:', error);
      message.error('删除失败');
    }
  };

  const handleEditTitle = (conv: Conversation) => {
    setEditingConvId(conv.id);
    setEditingTitle(conv.title || '');
  };

  const handleSaveTitle = async () => {
    if (!editingConvId || !editingTitle.trim()) {
      message.warning('请输入需求名称');
      return;
    }

    try {
      await conversationApi.updateTitle(editingConvId, editingTitle.trim());
      message.success('需求名称已更新');
      setEditingConvId(null);
      setEditingTitle('');
      await loadConversations();
    } catch (error: any) {
      console.error('Failed to update title:', error);
      message.error('更新失败');
    }
  };

  const handleCancelEdit = () => {
    setEditingConvId(null);
    setEditingTitle('');
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          color: 'success',
          icon: <CheckCircleOutlined />,
          text: '已完成',
        };
      case 'archived':
        return {
          color: 'default',
          icon: <FileTextOutlined />,
          text: '已归档',
        };
      default:
        return {
          color: 'processing',
          icon: <ClockCircleOutlined />,
          text: '进行中',
        };
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>需求管理</Title>
          <Text type="secondary">
            管理项目中的所有需求，每个需求对应一次完整的对话
            {conversations.filter(c => c.status === 'completed').length > 0 && (
              <>
                {' · '}
                <a onClick={() => navigate(`/project/${projectId}/knowledge`)}>
                  查看知识库中的 {conversations.filter(c => c.status === 'completed').length} 个已完成需求 →
                </a>
              </>
            )}
          </Text>
        </div>
        <Space>
          <Button
            icon={<BookOutlined />}
            onClick={() => navigate(`/project/${projectId}/knowledge`)}
          >
            查看知识库
          </Button>
          <Button
            type="primary"
            size="large"
            icon={<PlusOutlined />}
            onClick={() => setNewReqModalVisible(true)}
          >
            新建需求
          </Button>
        </Space>
      </div>

      {/* 统计信息 */}
      <div style={{ marginBottom: '24px' }}>
        <Space size="large">
          <Badge
            count={conversations.filter(c => c.status === 'active').length}
            showZero
            color="#1890ff"
            style={{ backgroundColor: '#1890ff' }}
          >
            <Card size="small" style={{ minWidth: '100px' }}>
              <Text type="secondary">进行中</Text>
            </Card>
          </Badge>
          <Badge
            count={conversations.filter(c => c.status === 'completed').length}
            showZero
            color="#52c41a"
            style={{ backgroundColor: '#52c41a' }}
          >
            <Card size="small" style={{ minWidth: '100px' }}>
              <Text type="secondary">已完成</Text>
            </Card>
          </Badge>
          <Badge
            count={conversations.filter(c => c.status === 'archived').length}
            showZero
            color="#d9d9d9"
            style={{ backgroundColor: '#d9d9d9' }}
          >
            <Card size="small" style={{ minWidth: '100px' }}>
              <Text type="secondary">已归档</Text>
            </Card>
          </Badge>
        </Space>
      </div>

      {/* 需求列表 */}
      {conversations.length === 0 ? (
        <Empty
          description={
            <div>
              <Text type="secondary">还没有创建任何需求</Text>
              <br />
              <Button
                type="link"
                onClick={() => setNewReqModalVisible(true)}
              >
                点击创建第一个需求
              </Button>
            </div>
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          style={{ marginTop: '60px' }}
        />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '16px' }}>
          {conversations.map((conv) => {
            const statusConfig = getStatusConfig(conv.status);
            return (
              <Card
                key={conv.id}
                hoverable
                onClick={() => navigate(`/project/${projectId}/requirement/${conv.id}`)}
                style={{
                  borderColor: conv.status === 'completed' ? '#52c41a' : undefined,
                }}
                actions={[
                  <Tooltip title="查看对话">
                    <MessageOutlined
                      key="chat"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/project/${projectId}/requirement/${conv.id}`);
                      }}
                    />
                  </Tooltip>,
                  <Tooltip title="编辑名称">
                    <EditOutlined
                      key="edit"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditTitle(conv);
                      }}
                    />
                  </Tooltip>,
                  conv.status === 'active' ? (
                    <Tooltip title="标记完成">
                      <Popconfirm
                        title="标记需求为已完成"
                        description="确认此需求已经讨论完毕？系统会自动生成摘要并归档到知识库。"
                        onConfirm={(e) => {
                          e?.stopPropagation();
                          handleMarkAsCompleted(conv.id);
                        }}
                        onCancel={(e) => e?.stopPropagation()}
                        okText="确认完成"
                        cancelText="取消"
                      >
                        <CheckCircleOutlined
                          key="complete"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>
                    </Tooltip>
                  ) : (
                    <Tooltip title={conv.status === 'completed' ? '已完成' : '已归档'}>
                      <CheckCircleOutlined
                        key="completed"
                        style={{ color: '#52c41a' }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Tooltip>
                  ),
                  <Tooltip title="删除需求">
                    <Popconfirm
                      title="删除需求"
                      description="确定要删除这个需求吗？所有对话记录将被删除。"
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        handleDeleteRequirement(conv.id);
                      }}
                      onCancel={(e) => e?.stopPropagation()}
                      okText="删除"
                      cancelText="取消"
                      okButtonProps={{ danger: true }}
                    >
                      <DeleteOutlined
                        key="delete"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Popconfirm>
                  </Tooltip>,
                ]}
              >
                <Card.Meta
                  title={
                    editingConvId === conv.id ? (
                      <Space.Compact style={{ width: '100%' }}>
                        <Input
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onPressEnter={handleSaveTitle}
                          placeholder="输入需求名称"
                          maxLength={50}
                          autoFocus
                          onClick={(e) => e.stopPropagation()}
                        />
                        <Button
                          type="primary"
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSaveTitle();
                          }}
                        >
                          保存
                        </Button>
                        <Button
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCancelEdit();
                          }}
                        >
                          取消
                        </Button>
                      </Space.Compact>
                    ) : (
                      <Space>
                        <Text strong ellipsis style={{ maxWidth: '200px' }}>
                          {conv.title || '未命名需求'}
                        </Text>
                        <Tag color={statusConfig.color} icon={statusConfig.icon}>
                          {statusConfig.text}
                        </Tag>
                      </Space>
                    )
                  }
                  description={
                    <div>
                      <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          消息数: {conv.message_count || 0}
                        </Text>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          创建于 {dayjs(conv.created_at).format('YYYY-MM-DD HH:mm')}
                        </Text>
                        {conv.updated_at !== conv.created_at && (
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            更新于 {dayjs(conv.updated_at).fromNow()}
                          </Text>
                        )}

                        {/* 显示需求摘要（如果有） */}
                        {conv.requirement_summary && (
                          <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                            <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                              <strong>需求概述：</strong>
                            </Text>
                            <Paragraph
                              ellipsis={{ rows: 2 }}
                              style={{ fontSize: '12px', margin: '4px 0 0 0' }}
                            >
                              {conv.requirement_summary.description}
                            </Paragraph>
                          </div>
                        )}
                      </Space>
                    </div>
                  }
                />
              </Card>
            );
          })}
        </div>
      )}

      {/* 新建需求弹窗 */}
      <Modal
        title="新建需求"
        open={newReqModalVisible}
        onOk={handleCreateRequirement}
        onCancel={() => {
          setNewReqModalVisible(false);
          setNewReqName('');
        }}
        confirmLoading={creating}
        okText="创建"
        cancelText="取消"
      >
        <div style={{ marginTop: '16px' }}>
          <Text>需求名称</Text>
          <Input
            placeholder="例如：用户登录功能"
            value={newReqName}
            onChange={(e) => setNewReqName(e.target.value)}
            onPressEnter={handleCreateRequirement}
            maxLength={50}
            showCount
            style={{ marginTop: '8px' }}
            autoFocus
          />
          <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '8px' }}>
            建议：用简短清晰的名称描述需求，后续可以在对话中详细讨论
          </Text>
        </div>
      </Modal>
    </div>
  );
};

export default Requirements;
