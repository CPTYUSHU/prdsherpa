import { useState, useEffect } from 'react';
import {
  Card,
  Space,
  Typography,
  Button,
  Collapse,
  Badge,
  message,
  Modal,
  Input,
  Spin,
  Tag,
  Tooltip,
} from 'antd';
import {
  FileTextOutlined,
  EditOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FileAddOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { prdApi } from '../services/api';
import type { PRDDraft, PRDSection } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface PRDPreviewProps {
  conversationId: string;
}

const PRDPreview = ({ conversationId }: PRDPreviewProps) => {
  const [prdDraft, setPrdDraft] = useState<PRDDraft | null>(null);
  const [loading, setLoading] = useState(false);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [savingSection, setSavingSection] = useState<string | null>(null);
  const [regeneratingSection, setRegeneratingSection] = useState<string | null>(null);

  // 加载 PRD 草稿
  const loadPRDDraft = async () => {
    try {
      setLoading(true);
      const draft = await prdApi.getDraft(conversationId);
      setPrdDraft(draft);
    } catch (error: any) {
      console.error('Failed to load PRD draft:', error);
      message.error('加载 PRD 草稿失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPRDDraft();
  }, [conversationId]);

  // 生成 PRD 大纲
  const handleGenerateOutline = async () => {
    try {
      setLoading(true);
      message.loading({ content: 'AI 正在生成 PRD 大纲...', key: 'generate', duration: 0 });
      const draft = await prdApi.generateOutline(conversationId);
      setPrdDraft(draft);
      message.success({ content: 'PRD 大纲生成成功！', key: 'generate' });
    } catch (error: any) {
      console.error('Failed to generate outline:', error);
      message.error({ content: '生成 PRD 大纲失败', key: 'generate' });
    } finally {
      setLoading(false);
    }
  };

  // 编辑章节
  const handleEditSection = (sectionKey: string, section: PRDSection) => {
    setEditingSection(sectionKey);
    setEditContent(section.content);
  };

  // 保存章节
  const handleSaveSection = async (sectionKey: string) => {
    try {
      setSavingSection(sectionKey);
      const draft = await prdApi.updateSection(conversationId, sectionKey, editContent);
      setPrdDraft(draft);
      setEditingSection(null);
      setEditContent('');
      message.success('章节保存成功');
    } catch (error: any) {
      console.error('Failed to save section:', error);
      message.error('保存失败');
    } finally {
      setSavingSection(null);
    }
  };

  // 重新生成章节
  const handleRegenerateSection = async (sectionKey: string) => {
    Modal.confirm({
      title: '重新生成章节',
      content: '确定要使用 AI 重新生成这个章节吗？当前内容将被覆盖。',
      okText: '确认生成',
      cancelText: '取消',
      onOk: async () => {
        try {
          setRegeneratingSection(sectionKey);
          message.loading({ content: 'AI 正在生成章节内容...', key: 'regen', duration: 0 });
          const draft = await prdApi.regenerateSection(conversationId, sectionKey);
          setPrdDraft(draft);
          message.success({ content: '章节生成成功！', key: 'regen' });
        } catch (error: any) {
          console.error('Failed to regenerate section:', error);
          message.error({ content: '生成失败', key: 'regen' });
        } finally {
          setRegeneratingSection(null);
        }
      },
    });
  };

  // 获取状态标签
  const getStatusBadge = (status: string) => {
    const configs: Record<string, { color: string; text: string; icon: any }> = {
      empty: { color: 'default', text: '未开始', icon: <FileAddOutlined /> },
      outline: { color: 'processing', text: '大纲', icon: <ClockCircleOutlined /> },
      draft: { color: 'warning', text: '草稿', icon: <EditOutlined /> },
      completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
    };
    const config = configs[status] || configs.empty;
    return <Tag icon={config.icon} color={config.color}>{config.text}</Tag>;
  };

  if (loading && !prdDraft) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: '16px' }}>
            <Text type="secondary">加载中...</Text>
          </div>
        </div>
      </Card>
    );
  }

  // 如果没有草稿，显示生成按钮
  if (!prdDraft || !prdDraft.sections || Object.keys(prdDraft.sections).length === 0) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <FileTextOutlined style={{ fontSize: '64px', color: '#1890ff', marginBottom: '16px' }} />
          <Title level={4}>PRD 实时预览</Title>
          <Paragraph type="secondary">
            基于当前对话，AI 将生成 PRD 大纲。<br />
            你可以随时编辑、补充或重新生成任何章节。
          </Paragraph>
          <Button
            type="primary"
            size="large"
            icon={<FileTextOutlined />}
            onClick={handleGenerateOutline}
            loading={loading}
          >
            生成 PRD 大纲
          </Button>
        </div>
      </Card>
    );
  }

  // 渲染章节列表
  const sections = Object.entries(prdDraft.sections);

  const collapseItems = sections.map(([sectionKey, section]) => ({
    key: sectionKey,
    label: (
      <Space>
        <Text strong>{section.title}</Text>
        {getStatusBadge(section.status)}
      </Space>
    ),
    extra: (
      <Space size="small" onClick={(e) => e.stopPropagation()}>
        <Tooltip title="编辑">
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditSection(sectionKey, section)}
          />
        </Tooltip>
        <Tooltip title="AI 重新生成">
          <Button
            type="text"
            size="small"
            icon={<ReloadOutlined />}
            loading={regeneratingSection === sectionKey}
            onClick={() => handleRegenerateSection(sectionKey)}
          />
        </Tooltip>
      </Space>
    ),
    children: (
      <div>
        {section.content ? (
          <div
            style={{
              padding: '16px',
              backgroundColor: '#fafafa',
              borderRadius: '4px',
              marginBottom: '8px',
            }}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {section.content}
            </ReactMarkdown>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
            <Text type="secondary">暂无内容，点击"AI 重新生成"按钮生成此章节</Text>
          </div>
        )}
        <Text type="secondary" style={{ fontSize: '12px' }}>
          最后更新：{new Date(section.updated_at).toLocaleString('zh-CN')}
        </Text>
      </div>
    ),
  }));

  return (
    <Card
      title={
        <Space>
          <FileTextOutlined />
          <Text strong>PRD 实时预览</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            v{prdDraft.version}
          </Text>
        </Space>
      }
      extra={
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadPRDDraft}
          >
            刷新
          </Button>
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            onClick={handleGenerateOutline}
            loading={loading}
          >
            重新生成大纲
          </Button>
        </Space>
      }
    >
      <Collapse
        items={collapseItems}
        defaultActiveKey={sections.map(([key]) => key)}
        bordered={false}
      />

      {/* 编辑章节模态框 */}
      <Modal
        title={`编辑：${prdDraft.sections[editingSection || '']?.title || ''}`}
        open={editingSection !== null}
        onOk={() => editingSection && handleSaveSection(editingSection)}
        onCancel={() => {
          setEditingSection(null);
          setEditContent('');
        }}
        confirmLoading={savingSection === editingSection}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <TextArea
          value={editContent}
          onChange={(e) => setEditContent(e.target.value)}
          rows={20}
          placeholder="使用 Markdown 格式编辑内容..."
          style={{ fontFamily: 'monospace', fontSize: '13px' }}
        />
        <div style={{ marginTop: '8px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            💡 提示：支持 Markdown 格式，包括标题、列表、粗体、斜体等
          </Text>
        </div>
      </Modal>
    </Card>
  );
};

export default PRDPreview;
