import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Button,
  Typography,
  Space,
  Spin,
  message,
  Descriptions,
  Tag,
  Modal,
  Input,
  Form,
  Select,
  Upload,
  Progress,
  Alert,
  Collapse,
  Tabs,
} from 'antd';
import {
  CheckOutlined,
  QuestionCircleOutlined,
  AppstoreOutlined,
  BgColorsOutlined,
  ToolOutlined,
  EditOutlined,
  UploadOutlined,
  FileOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ProjectOutlined,
  FolderOutlined,
  RiseOutlined,
  InfoCircleOutlined,
  FileTextOutlined,
  PictureOutlined,
  CodeOutlined,
  SearchOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { knowledgeApi, conversationApi, fileApi } from '../services/api';
import type { KnowledgeBase, UploadedFile } from '../types';
import KnowledgeSearch from '../components/KnowledgeSearch';
import { FileAnalysisProgress, KnowledgeBaseProgress } from '../components/LoadingStates';
import { useApiError } from '../hooks/useApiError';
import {
  estimateFileAnalysisTime,
  estimateKnowledgeBuildTime,
  ProgressCalculator,
  KnowledgeBuildProgress,
} from '../utils/progressEstimator';

const { Title, Text, Paragraph } = Typography;

type EditMode = 'system_overview' | 'ui_standards' | 'tech_conventions' | null;

const KnowledgeBasePage = () => {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const { handleUploadError, handleAnalysisError, showDetailedError } = useApiError();
  const [kb, setKb] = useState<KnowledgeBase | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [saving, setSaving] = useState(false);

  // 编辑状态
  const [editMode, setEditMode] = useState<EditMode>(null);
  const [editForm] = Form.useForm();

  // 问答状态
  const [answeringQuestion, setAnsweringQuestion] = useState<string | null>(null);
  const [answerText, setAnswerText] = useState('');

  // 补充资料状态
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [newFiles, setNewFiles] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [analyzingFiles, setAnalyzingFiles] = useState<Set<string>>(new Set());
  const [rebuildingKB, setRebuildingKB] = useState(false);

  // 进度状态
  const [fileProgressMap, setFileProgressMap] = useState<Map<string, { status: string; progress: number; estimatedTime?: number }>>(new Map());
  const [kbBuildStage, setKbBuildStage] = useState<'analyzing_files' | 'extracting_info' | 'building_structure' | 'completing'>('analyzing_files');
  const [kbProgress, setKbProgress] = useState<KnowledgeBuildProgress | null>(null);

  useEffect(() => {
    loadKnowledgeBase();
  }, [projectId]);

  const loadKnowledgeBase = async () => {
    if (!projectId) return;
    try {
      const data = await knowledgeApi.get(projectId);
      setKb(data);
    } catch (error: any) {
      console.error('Failed to load knowledge base:', error);
      message.error('加载知识库失败');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (section: EditMode) => {
    if (!kb) return;

    setEditMode(section);

    // 预填充表单
    switch (section) {
      case 'system_overview':
        editForm.setFieldsValue({
          product_type: kb.structured_data.system_overview?.product_type || '',
          description: kb.structured_data.system_overview?.description || '',
          core_modules: kb.structured_data.system_overview?.core_modules?.join(', ') || '',
        });
        break;
      case 'ui_standards':
        editForm.setFieldsValue({
          primary_colors: kb.structured_data.ui_standards?.primary_colors?.join(', ') || '',
          component_library: kb.structured_data.ui_standards?.component_library || '',
          layout_features: kb.structured_data.ui_standards?.layout_features?.join(', ') || '',
        });
        break;
      case 'tech_conventions':
        editForm.setFieldsValue({
          naming_style: kb.structured_data.tech_conventions?.naming_style || '',
          api_style: kb.structured_data.tech_conventions?.api_style || '',
        });
        break;
    }
  };

  const handleSaveEdit = async () => {
    if (!kb || !projectId || !editMode) return;

    try {
      const values = await editForm.validateFields();
      setSaving(true);

      // 构建更新的数据
      const updatedData = { ...kb.structured_data };

      switch (editMode) {
        case 'system_overview':
          updatedData.system_overview = {
            product_type: values.product_type,
            description: values.description,
            core_modules: values.core_modules
              ? values.core_modules.split(',').map((m: string) => m.trim()).filter(Boolean)
              : [],
          };
          break;
        case 'ui_standards':
          updatedData.ui_standards = {
            ...updatedData.ui_standards,
            primary_colors: values.primary_colors
              ? values.primary_colors.split(',').map((c: string) => c.trim()).filter(Boolean)
              : [],
            component_library: values.component_library,
            layout_features: values.layout_features
              ? values.layout_features.split(',').map((f: string) => f.trim()).filter(Boolean)
              : [],
          };
          break;
        case 'tech_conventions':
          updatedData.tech_conventions = {
            ...updatedData.tech_conventions,
            naming_style: values.naming_style,
            api_style: values.api_style,
          };
          break;
      }

      // 调用 API 更新
      const updated = await knowledgeApi.update(projectId, {
        structured_data: updatedData,
      });

      setKb(updated);
      message.success('保存成功');
      setEditMode(null);
      editForm.resetFields();
    } catch (error: any) {
      console.error('Failed to save:', error);
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleAnswerQuestion = async (question: string) => {
    if (!kb || !projectId || !answerText.trim()) return;

    try {
      setSaving(true);

      // 更新知识库，移除这个问题
      const updatedData = { ...kb.structured_data };
      const updatedQuestions = (updatedData.pending_questions || []).filter(
        q => q.question !== question
      );

      updatedData.pending_questions = updatedQuestions;

      // 调用更新接口保存
      const updated = await knowledgeApi.update(projectId, {
        structured_data: updatedData,
      });

      setKb(updated);
      setAnsweringQuestion(null);
      setAnswerText('');
      message.success('问题已标记为已回答');
    } catch (error: any) {
      console.error('Failed to save answer:', error);
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleConfirm = async () => {
    if (!projectId) return;
    try {
      setConfirming(true);
      await knowledgeApi.confirm(projectId, '产品经理');
      message.success('知识库已确认！');
      // 创建第一个对话
      const conversation = await conversationApi.create(projectId, '新需求讨论');
      navigate(`/project/${projectId}/chat/${conversation.id}`);
    } catch (error: any) {
      console.error('Failed to confirm knowledge base:', error);
      message.error('确认失败');
    } finally {
      setConfirming(false);
    }
  };

  // 处理文件选择
  const handleFileSelect = (file: File) => {
    setNewFiles([...newFiles, file]);
    return false; // 阻止自动上传
  };

  // 移除文件
  const handleRemoveFile = (file: File) => {
    setNewFiles(newFiles.filter(f => f !== file));
  };

  // 更新文件进度
  const updateFileProgress = (fileId: string, updates: { status: string; progress: number; estimatedTime?: number }) => {
    setFileProgressMap(prev => {
      const newMap = new Map(prev);
      newMap.set(fileId, updates);
      return newMap;
    });
  };

  // 上传并分析新文件
  const handleUploadNewFiles = async () => {
    if (!projectId || newFiles.length === 0) return;

    try {
      setUploading(true);
      const uploadedFilesList: UploadedFile[] = [];

      // 1. 上传所有文件
      for (const file of newFiles) {
        const tempId = `temp-${file.name}`;

        try {
          // 设置上传状态
          updateFileProgress(tempId, {
            status: 'uploading',
            progress: 0,
            estimatedTime: Math.ceil(file.size / (1024 * 1024) / 5) // 假设5MB/s
          });

          const uploaded = await fileApi.upload(projectId, file);
          uploadedFilesList.push(uploaded);

          // 上传完成，准备分析
          updateFileProgress(uploaded.id, {
            status: 'analyzing',
            progress: 30,
            estimatedTime: estimateFileAnalysisTime(file.type, file.size / (1024 * 1024))
          });

          // 移除临时ID
          setFileProgressMap(prev => {
            const newMap = new Map(prev);
            newMap.delete(tempId);
            return newMap;
          });
        } catch (error: any) {
          console.error(`Failed to upload ${file.name}:`, error);

          // 使用新的错误处理
          handleUploadError(
            file,
            error,
            async () => {
              // 重试上传
              try {
                const uploaded = await fileApi.upload(projectId, file);
                uploadedFilesList.push(uploaded);
                updateFileProgress(uploaded.id, { status: 'analyzing', progress: 30 });
              } catch (retryError) {
                updateFileProgress(tempId, { status: 'failed', progress: 0 });
              }
            }
          );

          updateFileProgress(tempId, { status: 'failed', progress: 0 });
        }
      }

      setUploadedFiles(uploadedFilesList);

      // 2. 分析所有已上传的文件
      for (const uploaded of uploadedFilesList) {
        try {
          setAnalyzingFiles(prev => new Set(prev).add(uploaded.id));

          await fileApi.analyze(uploaded.id);

          // 分析完成
          updateFileProgress(uploaded.id, { status: 'completed', progress: 100 });
          message.success(`${uploaded.filename} 分析完成`);
        } catch (error: any) {
          console.error(`Failed to analyze ${uploaded.filename}:`, error);

          // 使用新的错误处理
          handleAnalysisError(
            uploaded.filename,
            error,
            async () => {
              // 重试分析
              try {
                await fileApi.analyze(uploaded.id);
                updateFileProgress(uploaded.id, { status: 'completed', progress: 100 });
                message.success(`${uploaded.filename} 分析完成`);
              } catch (retryError) {
                updateFileProgress(uploaded.id, { status: 'failed', progress: 0 });
              }
            }
          );

          updateFileProgress(uploaded.id, { status: 'failed', progress: 0 });
        } finally {
          setAnalyzingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(uploaded.id);
            return newSet;
          });
        }
      }

      // 3. 重新构建知识库（增量）
      setRebuildingKB(true);

      // 初始化知识库构建进度
      const estimatedTime = estimateKnowledgeBuildTime(uploadedFilesList.length);
      const progress = new KnowledgeBuildProgress(estimatedTime);
      setKbProgress(progress);
      setKbBuildStage('analyzing_files');

      try {
        const fileIds = uploadedFilesList.map(f => f.id);

        // 模拟阶段进度
        setTimeout(() => setKbBuildStage('extracting_info'), estimatedTime * 0.3 * 1000);
        setTimeout(() => setKbBuildStage('building_structure'), estimatedTime * 0.7 * 1000);
        setTimeout(() => setKbBuildStage('completing'), estimatedTime * 0.9 * 1000);

        const updatedKB = await knowledgeApi.build(projectId, fileIds);
        setKb(updatedKB);
        message.success('知识库已更新！');

        // 关闭模态框，重置状态
        setUploadModalVisible(false);
        setNewFiles([]);
        setUploadedFiles([]);
        setFileProgressMap(new Map());
      } catch (error: any) {
        console.error('Failed to rebuild knowledge base:', error);

        showDetailedError(error, {
          title: '更新知识库失败',
        });
      } finally {
        setRebuildingKB(false);
        setKbProgress(null);
      }
    } catch (error: any) {
      console.error('Failed to upload files:', error);
      showDetailedError(error, {
        title: '上传失败',
      });
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!kb) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 20px' }}>
        <Text type="secondary">未找到知识库</Text>
      </div>
    );
  }

  const { structured_data } = kb;

  // 获取所有模块名称用于搜索筛选
  const availableModules = structured_data.feature_modules
    ? structured_data.feature_modules.map((m: any) => m.module_name)
    : [];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', overflow: 'auto', height: '100%' }}>
      <Space orientation="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Title level={2}>项目知识库</Title>
            <Text type="secondary">
              AI 已分析项目资料并生成结构化知识库，请确认或修正
            </Text>
          </div>
          <Button
            icon={<UploadOutlined />}
            onClick={() => setUploadModalVisible(true)}
          >
            补充资料
          </Button>
        </div>

        {/* Tabs: 知识库浏览 vs 搜索 */}
        <Tabs
          defaultActiveKey="browse"
          items={[
            {
              key: 'browse',
              label: (
                <span>
                  <DatabaseOutlined /> 浏览知识库
                </span>
              ),
              children: (
                <Space orientation="vertical" size="large" style={{ width: '100%' }}>
        {/* 上传建议提示 */}
        <Alert
          title="💡 如何让 AI 更好地理解你的项目？"
          description={
            <Collapse
              ghost
              bordered={false}
              items={[
                {
                  key: '1',
                  label: <Text strong>查看推荐上传的资料类型</Text>,
                  children: (
                    <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                      <div>
                        <Space>
                          <FileTextOutlined style={{ color: '#1890ff', fontSize: '18px' }} />
                          <Text strong>产品文档</Text>
                        </Space>
                        <div style={{ marginLeft: '26px', marginTop: '4px' }}>
                          <Text type="secondary">• 现有的 PRD、产品规格说明书</Text><br />
                          <Text type="secondary">• 业务流程文档、用户故事</Text><br />
                          <Text type="secondary">• 市场需求文档（MRD）</Text>
                        </div>
                      </div>

                      <div>
                        <Space>
                          <PictureOutlined style={{ color: '#52c41a', fontSize: '18px' }} />
                          <Text strong>设计稿与原型</Text>
                        </Space>
                        <div style={{ marginLeft: '26px', marginTop: '4px' }}>
                          <Text type="secondary">• UI 设计稿截图（高保真/低保真）</Text><br />
                          <Text type="secondary">• 交互原型图、流程图</Text><br />
                          <Text type="secondary">• 设计规范文档（颜色、字体、组件）</Text>
                        </div>
                      </div>

                      <div>
                        <Space>
                          <CodeOutlined style={{ color: '#722ed1', fontSize: '18px' }} />
                          <Text strong>技术文档</Text>
                        </Space>
                        <div style={{ marginLeft: '26px', marginTop: '4px' }}>
                          <Text type="secondary">• API 接口文档、数据库设计</Text><br />
                          <Text type="secondary">• 技术架构图、系统架构说明</Text><br />
                          <Text type="secondary">• 开发规范、代码约定</Text>
                        </div>
                      </div>

                      <div>
                        <Space>
                          <InfoCircleOutlined style={{ color: '#fa8c16', fontSize: '18px' }} />
                          <Text strong>其他参考资料</Text>
                        </Space>
                        <div style={{ marginLeft: '26px', marginTop: '4px' }}>
                          <Text type="secondary">• 竞品分析报告</Text><br />
                          <Text type="secondary">• 用户调研结果</Text><br />
                          <Text type="secondary">• 项目会议记录</Text>
                        </div>
                      </div>

                      <Alert
                        title="提示"
                        description="上传的资料越详细，AI 就能越准确地理解项目背景，生成更符合你需求的 PRD。支持 .md, .doc, .docx, .pdf, .txt, .png, .jpg 等格式。"
                        type="info"
                        showIcon
                        style={{ marginTop: '8px' }}
                      />
                    </Space>
                  ),
                },
              ]}
            />
          }
          type="info"
          showIcon
          closable
          style={{ marginBottom: '8px' }}
        />

        {/* 项目概览 - 新增统计看板 */}
        {structured_data.project_overview && (
          <Card
            title={
              <Space>
                <ProjectOutlined style={{ color: '#1890ff' }} />
                <Text strong>项目概览</Text>
              </Space>
            }
            style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}
            headStyle={{ color: 'white', borderBottom: '1px solid rgba(255,255,255,0.2)' }}
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {/* 产品信息 */}
              {(structured_data.project_overview.product_name || structured_data.project_overview.product_type) && (
                <Card size="small" style={{ background: 'rgba(255,255,255,0.95)' }}>
                  <Descriptions column={2} size="small">
                    {structured_data.project_overview.product_name && (
                      <Descriptions.Item label="产品名称" span={2}>
                        <Text strong style={{ fontSize: '16px' }}>{structured_data.project_overview.product_name}</Text>
                      </Descriptions.Item>
                    )}
                    {structured_data.project_overview.product_type && (
                      <Descriptions.Item label="产品类型">
                        {structured_data.project_overview.product_type}
                      </Descriptions.Item>
                    )}
                    {structured_data.project_overview.target_users && (
                      <Descriptions.Item label="目标用户">
                        {structured_data.project_overview.target_users}
                      </Descriptions.Item>
                    )}
                    {structured_data.project_overview.core_value && (
                      <Descriptions.Item label="核心价值" span={2}>
                        {structured_data.project_overview.core_value}
                      </Descriptions.Item>
                    )}
                    {structured_data.project_overview.business_model && (
                      <Descriptions.Item label="商业模式" span={2}>
                        {structured_data.project_overview.business_model}
                      </Descriptions.Item>
                    )}
                  </Descriptions>
                  {structured_data.project_overview.competitive_advantage && structured_data.project_overview.competitive_advantage.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <Text strong>竞争优势：</Text>
                      <div style={{ marginTop: '8px' }}>
                        <Space orientation="vertical" size="small">
                          {structured_data.project_overview.competitive_advantage.map((adv: string, idx: number) => (
                            <Text key={idx}>• {adv}</Text>
                          ))}
                        </Space>
                      </div>
                    </div>
                  )}
                </Card>
              )}

              {/* 项目描述 */}
              {structured_data.project_overview.description && (
                <div>
                  <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: '15px' }}>
                    {structured_data.project_overview.description}
                  </Text>
                </div>
              )}

              {/* 统计数据 */}
              {structured_data.project_overview.current_status && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginTop: '16px' }}>
                  {/* 总需求数 */}
                  <Card size="small" style={{ textAlign: 'center', background: 'rgba(255,255,255,0.95)' }}>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1890ff' }}>
                      {structured_data.project_overview.current_status.total_requirements || 0}
                    </div>
                    <Text type="secondary">已完成需求</Text>
                  </Card>

                  {/* 功能模块数 */}
                  {structured_data.project_overview.current_status.feature_count_by_module && (
                    <Card size="small" style={{ textAlign: 'center', background: 'rgba(255,255,255,0.95)' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#52c41a' }}>
                        {Object.keys(structured_data.project_overview.current_status.feature_count_by_module).length}
                      </div>
                      <Text type="secondary">功能模块</Text>
                    </Card>
                  )}

                  {/* 总功能数 */}
                  {structured_data.project_overview.current_status.feature_count_by_module && (
                    <Card size="small" style={{ textAlign: 'center', background: 'rgba(255,255,255,0.95)' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#722ed1' }}>
                        {Object.values(structured_data.project_overview.current_status.feature_count_by_module).reduce((a: number, b: number) => a + b, 0)}
                      </div>
                      <Text type="secondary">累计功能</Text>
                    </Card>
                  )}
                </div>
              )}

              {/* 各模块功能分布 */}
              {structured_data.project_overview.current_status?.feature_count_by_module && Object.keys(structured_data.project_overview.current_status.feature_count_by_module).length > 0 && (
                <Card size="small" style={{ background: 'rgba(255,255,255,0.95)', marginTop: '8px' }}>
                  <Text strong>功能模块分布</Text>
                  <div style={{ marginTop: '12px' }}>
                    <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                      {Object.entries(structured_data.project_overview.current_status.feature_count_by_module).map(([module, count]) => (
                        <div key={module} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Space>
                            <FolderOutlined style={{ color: '#1890ff' }} />
                            <Text>{module}</Text>
                          </Space>
                          <Tag color="blue">{count} 个功能</Tag>
                        </div>
                      ))}
                    </Space>
                  </div>
                </Card>
              )}
            </Space>
          </Card>
        )}

        {/* 功能模块 - 新增模块化展示 */}
        {structured_data.feature_modules && structured_data.feature_modules.length > 0 && (
          <Card
            title={
              <Space>
                <FolderOutlined style={{ color: '#52c41a' }} />
                <Text strong>功能模块</Text>
                <Tag color="success">{structured_data.feature_modules.length} 个模块</Tag>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              <Text type="secondary">
                项目功能按模块组织，每个模块包含相关的已完成功能
              </Text>
              {structured_data.feature_modules.map((module: any, idx: number) => (
                <Card
                  key={idx}
                  type="inner"
                  title={
                    <Space>
                      <FolderOutlined style={{ color: '#1890ff' }} />
                      <Text strong>{module.module_name}</Text>
                      {module.features && <Tag color="blue">{module.features.length} 个功能</Tag>}
                    </Space>
                  }
                  style={{ borderColor: '#91d5ff' }}
                >
                  {/* 模块描述 */}
                  {module.description && (
                    <Paragraph style={{ color: '#595959', marginBottom: '16px' }}>
                      {module.description}
                    </Paragraph>
                  )}

                  {/* 模块内的功能列表 */}
                  {module.features && module.features.length > 0 && (
                    <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                      {module.features.map((feature: any, fidx: number) => (
                        <Card
                          key={fidx}
                          size="small"
                          style={{ backgroundColor: '#f0f5ff', cursor: 'pointer' }}
                          hoverable
                          onClick={() => {
                            if (feature.conversation_id) {
                              navigate(`/project/${projectId}/requirement/${feature.conversation_id}`);
                            }
                          }}
                        >
                          <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                              <Space>
                                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                                <Text strong>{feature.name}</Text>
                                {feature.status === 'completed' && <Tag color="success">已完成</Tag>}
                              </Space>
                              {feature.completed_at && (
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                  {new Date(feature.completed_at).toLocaleDateString('zh-CN')}
                                </Text>
                              )}
                            </div>
                            {feature.description && (
                              <Text type="secondary" style={{ fontSize: '13px' }}>
                                {feature.description}
                              </Text>
                            )}
                            {feature.key_points && feature.key_points.length > 0 && (
                              <div style={{ paddingLeft: '20px' }}>
                                <Space orientation="vertical" size={2}>
                                  {feature.key_points.slice(0, 3).map((point: string, pidx: number) => (
                                    <Text key={pidx} type="secondary" style={{ fontSize: '12px' }}>
                                      • {point}
                                    </Text>
                                  ))}
                                  {feature.key_points.length > 3 && (
                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                      ... 还有 {feature.key_points.length - 3} 个要点
                                    </Text>
                                  )}
                                </Space>
                              </div>
                            )}
                          </Space>
                        </Card>
                      ))}
                    </Space>
                  )}
                </Card>
              ))}
            </Space>
          </Card>
        )}

        {/* 功能架构 */}
        {structured_data.functional_architecture && structured_data.functional_architecture.modules && structured_data.functional_architecture.modules.length > 0 && (
          <Card
            title={
              <Space>
                <AppstoreOutlined style={{ color: '#fa8c16' }} />
                <Text strong>功能架构</Text>
                <Tag color="orange">{structured_data.functional_architecture.modules.length} 个模块</Tag>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {structured_data.functional_architecture.modules.map((module: any, idx: number) => (
                <Card
                  key={idx}
                  type="inner"
                  title={
                    <Space>
                      <Text strong>{module.name}</Text>
                      {module.priority && <Tag color={module.priority === 'high' ? 'red' : module.priority === 'medium' ? 'orange' : 'default'}>{module.priority}</Tag>}
                    </Space>
                  }
                  style={{ borderColor: '#ffd591' }}
                >
                  {module.description && (
                    <Paragraph style={{ color: '#595959', marginBottom: '16px' }}>
                      {module.description}
                    </Paragraph>
                  )}
                  {module.features && module.features.length > 0 && (
                    <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                      <Text strong>功能列表：</Text>
                      {module.features.map((feature: any, fidx: number) => (
                        <Card key={fidx} size="small" style={{ backgroundColor: '#fffbe6' }}>
                          <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                            <Space>
                              <Text strong>{feature.name}</Text>
                              {feature.priority && <Tag color={feature.priority === 'P0' ? 'red' : feature.priority === 'P1' ? 'orange' : 'default'}>{feature.priority}</Tag>}
                            </Space>
                            {feature.description && <Text type="secondary">{feature.description}</Text>}
                            {feature.user_story && (
                              <div style={{ paddingLeft: '12px', borderLeft: '3px solid #faad14' }}>
                                <Text style={{ fontSize: '13px', color: '#8c8c8c' }}>{feature.user_story}</Text>
                              </div>
                            )}
                            {feature.acceptance_criteria && feature.acceptance_criteria.length > 0 && (
                              <div style={{ marginTop: '8px' }}>
                                <Text type="secondary" style={{ fontSize: '12px' }}>验收标准：</Text>
                                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                  {feature.acceptance_criteria.map((criteria: string, cidx: number) => (
                                    <li key={cidx} style={{ fontSize: '12px', color: '#595959' }}>{criteria}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </Space>
                        </Card>
                      ))}
                    </Space>
                  )}
                </Card>
              ))}
            </Space>
          </Card>
        )}

        {/* 用户体验 */}
        {structured_data.user_experience && (structured_data.user_experience.personas || structured_data.user_experience.user_journeys) && (
          <Card
            title={
              <Space>
                <InfoCircleOutlined style={{ color: '#13c2c2' }} />
                <Text strong>用户体验</Text>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {/* 用户画像 */}
              {structured_data.user_experience.personas && structured_data.user_experience.personas.length > 0 && (
                <div>
                  <Text strong>用户画像</Text>
                  <div style={{ marginTop: '12px' }}>
                    <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                      {structured_data.user_experience.personas.map((persona: any, idx: number) => (
                        <Card key={idx} size="small" style={{ backgroundColor: '#e6fffb' }}>
                          <Text strong>{persona.name}</Text>
                          {persona.description && <Paragraph style={{ marginTop: '8px', marginBottom: '8px' }}>{persona.description}</Paragraph>}
                          {persona.goals && persona.goals.length > 0 && (
                            <div style={{ marginTop: '8px' }}>
                              <Text type="secondary">目标：</Text>
                              <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                {persona.goals.map((goal: string, gidx: number) => (
                                  <li key={gidx} style={{ fontSize: '13px' }}>{goal}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {persona.pain_points && persona.pain_points.length > 0 && (
                            <div style={{ marginTop: '8px' }}>
                              <Text type="secondary">痛点：</Text>
                              <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                {persona.pain_points.map((pain: string, pidx: number) => (
                                  <li key={pidx} style={{ fontSize: '13px', color: '#ff4d4f' }}>{pain}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </Card>
                      ))}
                    </Space>
                  </div>
                </div>
              )}

              {/* 用户旅程 */}
              {structured_data.user_experience.user_journeys && structured_data.user_experience.user_journeys.length > 0 && (
                <div>
                  <Text strong>用户旅程</Text>
                  <div style={{ marginTop: '12px' }}>
                    <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                      {structured_data.user_experience.user_journeys.map((journey: any, idx: number) => (
                        <Card key={idx} size="small" style={{ backgroundColor: '#f0f5ff' }}>
                          <Text strong>{journey.scenario}</Text>
                          {journey.steps && journey.steps.length > 0 && (
                            <div style={{ marginTop: '12px' }}>
                              <Text type="secondary">步骤：</Text>
                              <ol style={{ margin: '8px 0', paddingLeft: '20px' }}>
                                {journey.steps.map((step: string, sidx: number) => (
                                  <li key={sidx} style={{ fontSize: '13px', marginBottom: '4px' }}>{step}</li>
                                ))}
                              </ol>
                            </div>
                          )}
                          {journey.touchpoints && journey.touchpoints.length > 0 && (
                            <div style={{ marginTop: '8px' }}>
                              <Text type="secondary">触点：</Text>
                              <Space wrap style={{ marginTop: '4px' }}>
                                {journey.touchpoints.map((touchpoint: string, tidx: number) => (
                                  <Tag key={tidx} color="blue">{touchpoint}</Tag>
                                ))}
                              </Space>
                            </div>
                          )}
                        </Card>
                      ))}
                    </Space>
                  </div>
                </div>
              )}

              {/* 关键交互 */}
              {structured_data.user_experience.key_interactions && structured_data.user_experience.key_interactions.length > 0 && (
                <div>
                  <Text strong>关键交互模式：</Text>
                  <Space wrap style={{ marginTop: '8px' }}>
                    {structured_data.user_experience.key_interactions.map((interaction: string, idx: number) => (
                      <Tag key={idx} color="cyan">{interaction}</Tag>
                    ))}
                  </Space>
                </div>
              )}
            </Space>
          </Card>
        )}

        {/* UI/UX 设计系统 */}
        {structured_data.ui_ux_design && (
          <Card
            title={
              <Space>
                <BgColorsOutlined style={{ color: '#eb2f96' }} />
                <Text strong>UI/UX 设计系统</Text>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {/* 设计系统 */}
              {structured_data.ui_ux_design.design_system && (
                <div>
                  <Text strong>设计系统</Text>
                  <Card size="small" style={{ marginTop: '12px', backgroundColor: '#fff0f6' }}>
                    <Descriptions column={2} size="small">
                      {structured_data.ui_ux_design.design_system.colors && (
                        <Descriptions.Item label="色彩" span={2}>
                          <Space wrap>
                            {Object.entries(structured_data.ui_ux_design.design_system.colors).map(([key, value]: [string, any]) => (
                              <div key={key}>
                                <Text type="secondary" style={{ fontSize: '12px' }}>{key}: </Text>
                                {Array.isArray(value) ? (
                                  <Space>
                                    {value.map((color: string, idx: number) => (
                                      <Tag key={idx} color={color}>{color}</Tag>
                                    ))}
                                  </Space>
                                ) : (
                                  <Tag color={value as string}>{value as string}</Tag>
                                )}
                              </div>
                            ))}
                          </Space>
                        </Descriptions.Item>
                      )}
                      {structured_data.ui_ux_design.design_system.typography && (
                        <Descriptions.Item label="字体" span={2}>
                          {JSON.stringify(structured_data.ui_ux_design.design_system.typography)}
                        </Descriptions.Item>
                      )}
                      {structured_data.ui_ux_design.design_system.spacing && (
                        <Descriptions.Item label="间距" span={2}>
                          {structured_data.ui_ux_design.design_system.spacing.unit && `基本单位: ${structured_data.ui_ux_design.design_system.spacing.unit}`}
                          {structured_data.ui_ux_design.design_system.spacing.scale && ` | ${structured_data.ui_ux_design.design_system.spacing.scale.join(', ')}`}
                        </Descriptions.Item>
                      )}
                    </Descriptions>
                  </Card>
                </div>
              )}

              {/* 组件 */}
              {structured_data.ui_ux_design.components && structured_data.ui_ux_design.components.length > 0 && (
                <div>
                  <Text strong>设计组件：</Text>
                  <div style={{ marginTop: '8px' }}>
                    <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                      {structured_data.ui_ux_design.components.map((component: any, idx: number) => (
                        <Card key={idx} size="small">
                          <Text strong>{component.name}</Text>
                          {component.variants && component.variants.length > 0 && (
                            <div style={{ marginTop: '4px' }}>
                              <Text type="secondary" style={{ fontSize: '12px' }}>变体: </Text>
                              <Space wrap>
                                {component.variants.map((variant: string, vidx: number) => (
                                  <Tag key={vidx} size="small">{variant}</Tag>
                                ))}
                              </Space>
                            </div>
                          )}
                          {component.usage && (
                            <Text type="secondary" style={{ display: 'block', marginTop: '4px', fontSize: '12px' }}>
                              使用场景: {component.usage}
                            </Text>
                          )}
                        </Card>
                      ))}
                    </Space>
                  </div>
                </div>
              )}

              {/* 布局模式 */}
              {structured_data.ui_ux_design.layout_patterns && structured_data.ui_ux_design.layout_patterns.length > 0 && (
                <div>
                  <Text strong>布局模式：</Text>
                  <Space wrap style={{ marginTop: '8px' }}>
                    {structured_data.ui_ux_design.layout_patterns.map((pattern: string, idx: number) => (
                      <Tag key={idx} color="purple">{pattern}</Tag>
                    ))}
                  </Space>
                </div>
              )}

              {/* 响应式策略 */}
              {structured_data.ui_ux_design.responsive_strategy && (
                <div>
                  <Text strong>响应式策略：</Text>
                  <Paragraph style={{ marginTop: '8px' }}>{structured_data.ui_ux_design.responsive_strategy}</Paragraph>
                </div>
              )}

              {/* 无障碍特性 */}
              {structured_data.ui_ux_design.accessibility && structured_data.ui_ux_design.accessibility.length > 0 && (
                <div>
                  <Text strong>无障碍特性：</Text>
                  <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                    {structured_data.ui_ux_design.accessibility.map((item: string, idx: number) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Space>
          </Card>
        )}

        {/* 数据模型 */}
        {structured_data.data_model && structured_data.data_model.entities && structured_data.data_model.entities.length > 0 && (
          <Card
            title={
              <Space>
                <DatabaseOutlined style={{ color: '#722ed1' }} />
                <Text strong>数据模型</Text>
                <Tag color="purple">{structured_data.data_model.entities.length} 个实体</Tag>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {structured_data.data_model.entities.map((entity: any, idx: number) => (
                <Card
                  key={idx}
                  type="inner"
                  title={<Text strong>{entity.name}</Text>}
                  style={{ borderColor: '#d3adf7' }}
                >
                  {entity.description && (
                    <Paragraph style={{ marginBottom: '12px', color: '#595959' }}>{entity.description}</Paragraph>
                  )}
                  {entity.fields && entity.fields.length > 0 && (
                    <div>
                      <Text strong>字段：</Text>
                      <div style={{ marginTop: '8px' }}>
                        <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                          {entity.fields.map((field: any, fidx: number) => (
                            <div key={fidx} style={{ padding: '8px', backgroundColor: '#f9f0ff', borderRadius: '4px' }}>
                              <Space>
                                <Text strong>{field.name}</Text>
                                <Tag color="purple">{field.type}</Tag>
                                {field.required && <Tag color="red">必填</Tag>}
                              </Space>
                              {field.description && (
                                <Text type="secondary" style={{ display: 'block', marginTop: '4px', fontSize: '12px' }}>
                                  {field.description}
                                </Text>
                              )}
                              {field.validation && (
                                <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
                                  验证: {field.validation}
                                </Text>
                              )}
                              {field.example && (
                                <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
                                  示例: {field.example}
                                </Text>
                              )}
                            </div>
                          ))}
                        </Space>
                      </div>
                    </div>
                  )}
                  {entity.relationships && entity.relationships.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <Text strong>关系：</Text>
                      <div style={{ marginTop: '8px' }}>
                        {entity.relationships.map((rel: any, ridx: number) => (
                          <Tag key={ridx} color="cyan" style={{ marginBottom: '4px' }}>
                            {rel.type} → {rel.target} {rel.description && `(${rel.description})`}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </Space>
          </Card>
        )}

        {/* 业务规则 */}
        {structured_data.business_rules && (
          <Card
            title={
              <Space>
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                <Text strong>业务规则</Text>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {/* 规则 */}
              {structured_data.business_rules.rules && structured_data.business_rules.rules.length > 0 && (
                <div>
                  <Text strong>业务规则：</Text>
                  <div style={{ marginTop: '12px' }}>
                    <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                      {structured_data.business_rules.rules.map((rule: any, idx: number) => (
                        <Card key={idx} size="small" style={{ backgroundColor: '#f6ffed' }}>
                          <Text strong>{rule.name}</Text>
                          {rule.description && <Paragraph style={{ marginTop: '4px' }}>{rule.description}</Paragraph>}
                          {rule.conditions && rule.conditions.length > 0 && (
                            <div style={{ marginTop: '8px' }}>
                              <Text type="secondary">条件: </Text>
                              {rule.conditions.map((cond: string, cidx: number) => (
                                <Tag key={cidx} style={{ marginLeft: '4px' }}>{cond}</Tag>
                              ))}
                            </div>
                          )}
                          {rule.actions && rule.actions.length > 0 && (
                            <div style={{ marginTop: '4px' }}>
                              <Text type="secondary">动作: </Text>
                              {rule.actions.map((action: string, aidx: number) => (
                                <Tag key={aidx} color="green" style={{ marginLeft: '4px' }}>{action}</Tag>
                              ))}
                            </div>
                          )}
                        </Card>
                      ))}
                    </Space>
                  </div>
                </div>
              )}

              {/* 权限 */}
              {structured_data.business_rules.permissions && structured_data.business_rules.permissions.length > 0 && (
                <div>
                  <Text strong>权限控制：</Text>
                  <div style={{ marginTop: '8px' }}>
                    {structured_data.business_rules.permissions.map((perm: any, idx: number) => (
                      <div key={idx} style={{ marginBottom: '8px' }}>
                        <Tag color="blue">{perm.role}</Tag>
                        <Text type="secondary"> 可以: </Text>
                        {perm.permissions && perm.permissions.map((p: string, pidx: number) => (
                          <Tag key={pidx} style={{ marginLeft: '4px' }}>{p}</Tag>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 工作流 */}
              {structured_data.business_rules.workflows && structured_data.business_rules.workflows.length > 0 && (
                <div>
                  <Text strong>工作流：</Text>
                  <div style={{ marginTop: '12px' }}>
                    <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                      {structured_data.business_rules.workflows.map((workflow: any, idx: number) => (
                        <Card key={idx} size="small">
                          <Text strong>{workflow.name}</Text>
                          {workflow.steps && workflow.steps.length > 0 && (
                            <ol style={{ margin: '8px 0', paddingLeft: '20px' }}>
                              {workflow.steps.map((step: string, sidx: number) => (
                                <li key={sidx} style={{ fontSize: '13px' }}>{step}</li>
                              ))}
                            </ol>
                          )}
                        </Card>
                      ))}
                    </Space>
                  </div>
                </div>
              )}
            </Space>
          </Card>
        )}

        {/* 非功能需求 */}
        {structured_data.non_functional_requirements && (
          <Card
            title={
              <Space>
                <RiseOutlined style={{ color: '#fa541c' }} />
                <Text strong>非功能需求</Text>
              </Space>
            }
          >
            <Descriptions column={1} size="small">
              {structured_data.non_functional_requirements.performance && (
                <Descriptions.Item label="性能要求">
                  {Object.entries(structured_data.non_functional_requirements.performance).map(([key, value]) => (
                    <div key={key}>
                      <Text>{key}: {value as string}</Text>
                    </div>
                  ))}
                </Descriptions.Item>
              )}
              {structured_data.non_functional_requirements.reliability && (
                <Descriptions.Item label="可靠性">
                  {Object.entries(structured_data.non_functional_requirements.reliability).map(([key, value]) => (
                    <div key={key}>
                      <Text>{key}: {value as string}</Text>
                    </div>
                  ))}
                </Descriptions.Item>
              )}
              {structured_data.non_functional_requirements.scalability && (
                <Descriptions.Item label="可扩展性">
                  {Object.entries(structured_data.non_functional_requirements.scalability).map(([key, value]) => (
                    <div key={key}>
                      <Text>{key}: {value as string}</Text>
                    </div>
                  ))}
                </Descriptions.Item>
              )}
              {structured_data.non_functional_requirements.compatibility && (
                <Descriptions.Item label="兼容性">
                  <div>
                    {structured_data.non_functional_requirements.compatibility.browsers && (
                      <div><Text strong>浏览器: </Text>{structured_data.non_functional_requirements.compatibility.browsers.join(', ')}</div>
                    )}
                    {structured_data.non_functional_requirements.compatibility.devices && (
                      <div><Text strong>设备: </Text>{structured_data.non_functional_requirements.compatibility.devices.join(', ')}</div>
                    )}
                    {structured_data.non_functional_requirements.compatibility.os && (
                      <div><Text strong>操作系统: </Text>{structured_data.non_functional_requirements.compatibility.os.join(', ')}</div>
                    )}
                  </div>
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        )}

        {/* 系统概览 */}
        {structured_data.system_overview && (
          <Card
            title={
              <Space>
                <AppstoreOutlined />
                <Text strong>系统概览</Text>
              </Space>
            }
            extra={
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEdit('system_overview')}
              >
                编辑
              </Button>
            }
          >
            <Descriptions column={1}>
              {structured_data.system_overview.product_type && (
                <Descriptions.Item label="产品类型">
                  {structured_data.system_overview.product_type}
                </Descriptions.Item>
              )}
              {structured_data.system_overview.description && (
                <Descriptions.Item label="描述">
                  {structured_data.system_overview.description}
                </Descriptions.Item>
              )}
              {structured_data.system_overview.core_modules && (
                <Descriptions.Item label="核心模块">
                  <Space wrap>
                    {structured_data.system_overview.core_modules.map((module, idx) => (
                      <Tag key={idx} color="blue">{module}</Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        )}

        {/* UI 规范 */}
        {structured_data.ui_standards && (
          <Card
            title={
              <Space>
                <BgColorsOutlined />
                <Text strong>UI 规范</Text>
              </Space>
            }
            extra={
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEdit('ui_standards')}
              >
                编辑
              </Button>
            }
          >
            <Descriptions column={1}>
              {structured_data.ui_standards.primary_colors && (
                <Descriptions.Item label="主色调">
                  <Space>
                    {structured_data.ui_standards.primary_colors.map((color, idx) => (
                      <Tag key={idx} color={color}>{color}</Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
              {structured_data.ui_standards.component_library && (
                <Descriptions.Item label="组件库">
                  {structured_data.ui_standards.component_library}
                </Descriptions.Item>
              )}
              {structured_data.ui_standards.layout_features && (
                <Descriptions.Item label="布局特征">
                  <Space wrap>
                    {structured_data.ui_standards.layout_features.map((feature, idx) => (
                      <Tag key={idx}>{feature}</Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        )}

        {/* 技术架构 */}
        {(structured_data.tech_conventions || structured_data.tech_architecture) && (
          <Card
            title={
              <Space>
                <ToolOutlined />
                <Text strong>技术架构</Text>
              </Space>
            }
            extra={
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEdit('tech_conventions')}
              >
                编辑
              </Button>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {/* 技术约定 */}
              {structured_data.tech_conventions && (
                <Descriptions column={1}>
                  {structured_data.tech_conventions.naming_style && (
                    <Descriptions.Item label="命名风格">
                      {structured_data.tech_conventions.naming_style}
                    </Descriptions.Item>
                  )}
                  {structured_data.tech_conventions.api_style && (
                    <Descriptions.Item label="API 风格">
                      {structured_data.tech_conventions.api_style}
                    </Descriptions.Item>
                  )}
                </Descriptions>
              )}

              {/* 技术模式 */}
              {structured_data.tech_architecture?.patterns && structured_data.tech_architecture.patterns.length > 0 && (
                <div>
                  <Text strong>技术模式</Text>
                  <div style={{ marginTop: '8px' }}>
                    <Space wrap>
                      {structured_data.tech_architecture.patterns.map((pattern: string, idx: number) => (
                        <Tag key={idx} color="purple" icon={<RiseOutlined />}>
                          {pattern}
                        </Tag>
                      ))}
                    </Space>
                  </div>
                </div>
              )}
            </Space>
          </Card>
        )}

        {/* 已完成需求 */}
        {structured_data.completed_requirements && structured_data.completed_requirements.length > 0 && (
          <Card
            title={
              <Space>
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                <Text strong>已完成需求</Text>
                <Tag color="success">{structured_data.completed_requirements.length} 个需求</Tag>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              <Text type="secondary">
                以下是已经确认和完成的需求，新需求设计时请参考这些内容，避免冲突或重复
              </Text>
              {structured_data.completed_requirements.map((req: any, idx: number) => (
                <Card
                  key={idx}
                  size="small"
                  type="inner"
                  style={{ backgroundColor: '#f6ffed', borderColor: '#b7eb8f' }}
                  hoverable
                  onClick={() => {
                    if (req.conversation_id) {
                      navigate(`/project/${projectId}/requirement/${req.conversation_id}`);
                    }
                  }}
                >
                  <Space orientation="vertical" style={{ width: '100%' }} size="small">
                    {/* 标题和时间 */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Space>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        <Text strong style={{ fontSize: '15px' }}>{req.title || '未命名需求'}</Text>
                        {req.prd_generated && <Tag color="blue">已生成PRD</Tag>}
                      </Space>
                      {req.archived_at && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          <ClockCircleOutlined /> {new Date(req.archived_at).toLocaleDateString('zh-CN')}
                        </Text>
                      )}
                    </div>

                    {/* 描述 */}
                    {req.description && (
                      <Paragraph
                        style={{ marginBottom: 8, color: '#595959' }}
                        ellipsis={{ rows: 2, expandable: true, symbol: '展开' }}
                      >
                        {req.description}
                      </Paragraph>
                    )}

                    {/* 关键要点 */}
                    {req.key_points && req.key_points.length > 0 && (
                      <div>
                        <Text type="secondary" style={{ fontSize: '12px' }}>关键要点：</Text>
                        <div style={{ marginTop: '4px' }}>
                          <Space orientation="vertical" size={2}>
                            {req.key_points.map((point: string, pidx: number) => (
                              <Text key={pidx} style={{ fontSize: '13px' }}>
                                • {point}
                              </Text>
                            ))}
                          </Space>
                        </div>
                      </div>
                    )}
                  </Space>
                </Card>
              ))}
            </Space>
          </Card>
        )}

        {/* 待确认问题 */}
        {structured_data.pending_questions && structured_data.pending_questions.length > 0 && (
          <Card
            title={
              <Space>
                <QuestionCircleOutlined />
                <Text strong>待确认问题</Text>
              </Space>
            }
          >
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {structured_data.pending_questions.map((q, idx) => (
                <Card
                  key={idx}
                  size="small"
                  type="inner"
                  style={{ backgroundColor: '#fff7e6' }}
                >
                  <Space orientation="vertical" style={{ width: '100%' }}>
                    <Space>
                      <Tag color="orange">{q.category}</Tag>
                      <Text strong>{q.question}</Text>
                    </Space>
                    {answeringQuestion === q.question ? (
                      <Space.Compact style={{ width: '100%' }}>
                        <Input.TextArea
                          rows={2}
                          placeholder="输入你的回答..."
                          value={answerText}
                          onChange={(e) => setAnswerText(e.target.value)}
                          style={{ flex: 1 }}
                        />
                        <Space orientation="vertical">
                          <Button
                            type="primary"
                            size="small"
                            onClick={() => handleAnswerQuestion(q.question)}
                            loading={saving}
                          >
                            保存
                          </Button>
                          <Button
                            size="small"
                            onClick={() => {
                              setAnsweringQuestion(null);
                              setAnswerText('');
                            }}
                          >
                            取消
                          </Button>
                        </Space>
                      </Space.Compact>
                    ) : (
                      <Button
                        size="small"
                        onClick={() => setAnsweringQuestion(q.question)}
                      >
                        回答问题
                      </Button>
                    )}
                  </Space>
                </Card>
              ))}
            </Space>
          </Card>
        )}

        {/* 操作按钮 */}
        <div style={{ textAlign: 'center', paddingBottom: '40px' }}>
          <Button
            type="primary"
            size="large"
            icon={<CheckOutlined />}
            loading={confirming}
            onClick={handleConfirm}
          >
            确认知识库，开始写需求
          </Button>
        </div>
                </Space>
              ),
            },
            {
              key: 'search',
              label: (
                <span>
                  <SearchOutlined /> 搜索
                </span>
              ),
              children: (
                <KnowledgeSearch
                  projectId={projectId!}
                  availableModules={availableModules}
                />
              ),
            },
          ]}
        />
      </Space>

      {/* 编辑模态框 */}
      <Modal
        title={
          editMode === 'system_overview' ? '编辑系统概览' :
          editMode === 'ui_standards' ? '编辑 UI 规范' :
          editMode === 'tech_conventions' ? '编辑技术约定' :
          '编辑'
        }
        open={editMode !== null}
        onOk={handleSaveEdit}
        onCancel={() => {
          setEditMode(null);
          editForm.resetFields();
        }}
        confirmLoading={saving}
        width={600}
      >
        <Form
          form={editForm}
          layout="vertical"
          style={{ marginTop: 24 }}
        >
          {editMode === 'system_overview' && (
            <>
              <Form.Item
                label="产品类型"
                name="product_type"
                rules={[{ required: true, message: '请输入产品类型' }]}
              >
                <Input placeholder="例如：内容管理系统、电商后台..." />
              </Form.Item>
              <Form.Item
                label="描述"
                name="description"
              >
                <Input.TextArea rows={3} placeholder="产品简介..." />
              </Form.Item>
              <Form.Item
                label="核心模块"
                name="core_modules"
                help="多个模块用逗号分隔"
              >
                <Input placeholder="例如：用户管理, 内容发布, 数据统计" />
              </Form.Item>
            </>
          )}

          {editMode === 'ui_standards' && (
            <>
              <Form.Item
                label="主色调"
                name="primary_colors"
                help="多个颜色用逗号分隔"
              >
                <Input placeholder="例如：#1890ff, #52c41a" />
              </Form.Item>
              <Form.Item
                label="组件库"
                name="component_library"
              >
                <Input placeholder="例如：Ant Design, Element UI..." />
              </Form.Item>
              <Form.Item
                label="布局特征"
                name="layout_features"
                help="多个特征用逗号分隔"
              >
                <Input placeholder="例如：左右两栏, 顶部导航, 卡片式" />
              </Form.Item>
            </>
          )}

          {editMode === 'tech_conventions' && (
            <>
              <Form.Item
                label="命名风格"
                name="naming_style"
              >
                <Select placeholder="选择命名风格">
                  <Select.Option value="camelCase">驼峰命名 (camelCase)</Select.Option>
                  <Select.Option value="snake_case">下划线命名 (snake_case)</Select.Option>
                  <Select.Option value="PascalCase">帕斯卡命名 (PascalCase)</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item
                label="API 风格"
                name="api_style"
              >
                <Select placeholder="选择 API 风格">
                  <Select.Option value="RESTful">RESTful</Select.Option>
                  <Select.Option value="GraphQL">GraphQL</Select.Option>
                  <Select.Option value="RPC">RPC</Select.Option>
                </Select>
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>

      {/* 补充资料模态框 */}
      <Modal
        title="补充项目资料"
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false);
          setNewFiles([]);
          setUploadedFiles([]);
        }}
        footer={[
          <Button
            key="cancel"
            onClick={() => {
              setUploadModalVisible(false);
              setNewFiles([]);
              setUploadedFiles([]);
            }}
          >
            取消
          </Button>,
          <Button
            key="submit"
            type="primary"
            loading={uploading || rebuildingKB}
            disabled={newFiles.length === 0}
            onClick={handleUploadNewFiles}
          >
            {uploading ? '上传中...' : rebuildingKB ? '更新知识库中...' : '开始分析'}
          </Button>,
        ]}
        width={600}
      >
        <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
          <Text type="secondary">
            上传新的项目资料，AI 将分析后增量更新知识库
          </Text>

          {/* 建议上传内容提示 */}
          <Alert
            message="💡 推荐上传"
            description={
              <Space orientation="vertical" size="small">
                <Text>• <Text strong>产品文档：</Text>PRD、业务流程、用户故事</Text>
                <Text>• <Text strong>设计稿：</Text>UI 截图、原型图、设计规范</Text>
                <Text>• <Text strong>技术文档：</Text>API 文档、架构图、开发规范</Text>
                <Text>• <Text strong>其他资料：</Text>竞品分析、用户调研、会议记录</Text>
              </Space>
            }
            type="info"
            showIcon
            style={{ fontSize: '12px' }}
          />

          {/* 文件上传区 */}
          <Upload
            beforeUpload={handleFileSelect}
            fileList={newFiles.map((file, index) => ({
              uid: `${index}`,
              name: file.name,
              status: 'done' as const,
              size: file.size,
            }))}
            onRemove={(file) => {
              const index = parseInt(file.uid);
              handleRemoveFile(newFiles[index]);
            }}
            multiple
            disabled={uploading || rebuildingKB}
          >
            <Button
              icon={<UploadOutlined />}
              disabled={uploading || rebuildingKB}
              block
            >
              选择文件
            </Button>
          </Upload>

          {/* 支持格式提示 */}
          <Text type="secondary" style={{ fontSize: '12px' }}>
            支持格式：.md, .doc, .docx, .pptx, .pdf, .txt, .png, .jpg, .jpeg（单文件最大 200MB）
          </Text>

          {/* 文件分析进度 */}
          {uploadedFiles.length > 0 && (
            <Card size="small" title="文件分析进度">
              <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                {uploadedFiles.map((file) => {
                  const progress = fileProgressMap.get(file.id);
                  const status = progress?.status || (analyzingFiles.has(file.id) ? 'analyzing' : 'completed');

                  return (
                    <FileAnalysisProgress
                      key={file.id}
                      fileName={file.filename}
                      status={status as any}
                      progress={progress?.progress || (status === 'completed' ? 100 : 50)}
                      estimatedTime={progress?.estimatedTime}
                    />
                  );
                })}
              </Space>
            </Card>
          )}

          {/* 知识库构建进度 */}
          {rebuildingKB && kbProgress && (
            <KnowledgeBaseProgress
              stage={kbBuildStage}
              filesProcessed={uploadedFiles.filter(f => fileProgressMap.get(f.id)?.status === 'completed').length}
              totalFiles={uploadedFiles.length}
              estimatedTime={kbProgress.getRemainingTime()}
            />
          )}
        </Space>
      </Modal>
    </div>
  );
};

export default KnowledgeBasePage;
