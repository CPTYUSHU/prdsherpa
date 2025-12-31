import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Form,
  Input,
  Button,
  Upload,
  Card,
  Typography,
  Space,
  message,
  Progress,
  Spin,
  Tag,
} from 'antd';
import { InboxOutlined, DeleteOutlined, CheckCircleOutlined, LoadingOutlined, FileOutlined, EyeOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd';
import { projectApi, fileApi, knowledgeApi } from '../services/api';
import { useApp } from '../contexts/AppContext';
import type { UploadedFile } from '../types';
import { useApiError } from '../hooks/useApiError';
import FileBatchActions from '../components/FileBatchActions';
import FilePreview from '../components/FilePreview/FilePreview';

const { Title, Text } = Typography;
const { Dragger } = Upload;

type FileAnalysisStatus = 'pending' | 'uploading' | 'analyzing' | 'completed' | 'failed';

interface FileWithStatus {
  file: UploadFile;
  uploadedFile?: UploadedFile;
  status: FileAnalysisStatus;
  error?: string;
}

const NewProject = () => {
  const navigate = useNavigate();
  const { refreshProjects } = useApp();
  const { handleUploadError, handleAnalysisError, showDetailedError } = useApiError();
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [processing, setProcessing] = useState(false);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [filesWithStatus, setFilesWithStatus] = useState<FileWithStatus[]>([]);
  const [buildingKB, setBuildingKB] = useState(false);

  // 文件选择和预览状态
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  const [previewFile, setPreviewFile] = useState<UploadFile | null>(null);

  const updateFileStatus = (index: number, updates: Partial<FileWithStatus>) => {
    setFilesWithStatus(prev => {
      const newList = [...prev];
      newList[index] = { ...newList[index], ...updates };
      return newList;
    });
  };

  // 处理批量删除
  const handleBatchDelete = () => {
    const newFileList = fileList.filter(file => !selectedFileIds.includes(file.uid));
    setFileList(newFileList);
    setSelectedFileIds([]);
    message.success(`已删除 ${selectedFileIds.length} 个文件`);
  };

  // 处理文件预览
  const handlePreview = (file: UploadFile) => {
    setPreviewFile(file);
  };

  const handleCreateProject = async (values: any) => {
    try {
      setProcessing(true);

      // 创建项目
      const project = await projectApi.create({
        name: values.name,
        description: values.description,
      });
      setProjectId(project.id);
      await refreshProjects();

      // 如果没有文件，直接跳转
      if (fileList.length === 0) {
        message.success('项目创建成功！');
        navigate(`/project/${project.id}/chat`);
        return;
      }

      // 初始化文件状态列表
      const initialFiles: FileWithStatus[] = fileList.map(f => ({
        file: f,
        status: 'pending' as FileAnalysisStatus,
      }));
      setFilesWithStatus(initialFiles);

      const uploadedFiles: UploadedFile[] = [];

      // 1. 上传所有文件
      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        if (!file.originFileObj) continue;

        try {
          updateFileStatus(i, { status: 'uploading' });
          const uploaded = await fileApi.upload(project.id, file.originFileObj);
          uploadedFiles.push(uploaded);
          updateFileStatus(i, {
            status: 'analyzing',
            uploadedFile: uploaded,
          });
        } catch (error: any) {
          console.error(`Upload failed for ${file.name}:`, error);

          // 使用新的错误处理
          handleUploadError(
            file.originFileObj,
            error,
            async () => {
              // 重试上传
              updateFileStatus(i, { status: 'uploading', error: undefined });
              try {
                const uploaded = await fileApi.upload(project.id, file.originFileObj!);
                uploadedFiles.push(uploaded);
                updateFileStatus(i, {
                  status: 'analyzing',
                  uploadedFile: uploaded,
                });
              } catch (retryError: any) {
                updateFileStatus(i, {
                  status: 'failed',
                  error: '上传失败',
                });
              }
            }
          );

          updateFileStatus(i, {
            status: 'failed',
            error: '上传失败',
          });
        }
      }

      // 2. 分析所有已上传的文件
      for (let i = 0; i < uploadedFiles.length; i++) {
        const uploaded = uploadedFiles[i];
        const fileIndex = filesWithStatus.findIndex(
          f => f.uploadedFile?.id === uploaded.id
        );

        try {
          await fileApi.analyze(uploaded.id);
          updateFileStatus(fileIndex, { status: 'completed' });
        } catch (error: any) {
          console.error(`Analysis failed for ${uploaded.filename}:`, error);

          // 使用新的错误处理
          handleAnalysisError(
            uploaded.filename,
            error,
            async () => {
              // 重试分析
              updateFileStatus(fileIndex, { status: 'analyzing', error: undefined });
              try {
                await fileApi.analyze(uploaded.id);
                updateFileStatus(fileIndex, { status: 'completed' });
                message.success(`${uploaded.filename} 分析成功`);
              } catch (retryError: any) {
                updateFileStatus(fileIndex, {
                  status: 'failed',
                  error: '分析失败',
                });
              }
            }
          );

          updateFileStatus(fileIndex, {
            status: 'failed',
            error: '分析失败',
          });
        }
      }

      // 3. 构建知识库
      if (uploadedFiles.length > 0) {
        setBuildingKB(true);
        try {
          await knowledgeApi.build(
            project.id,
            uploadedFiles.map((f) => f.id)
          );
          message.success('项目创建成功！');

          // 延迟跳转，让用户看到完成状态
          setTimeout(() => {
            navigate(`/project/${project.id}/knowledge`);
          }, 1000);
        } catch (error: any) {
          console.error('Failed to build knowledge base:', error);
          message.error('构建知识库失败');
        } finally {
          setBuildingKB(false);
        }
      }
    } catch (error: any) {
      console.error('Failed to create project:', error);
      message.error(error.response?.data?.detail || '创建项目失败');
    } finally {
      setProcessing(false);
    }
  };

  const uploadProps = {
    multiple: true,
    fileList,
    beforeUpload: (file: File) => {
      // 检查文件大小 (200MB)
      if (file.size > 200 * 1024 * 1024) {
        message.error(`${file.name} 文件大小超过 200MB`);
        return false;
      }
      // 检查文件类型
      const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/markdown',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/gif',
        'image/webp',
      ];
      if (!allowedTypes.includes(file.type)) {
        message.error(`${file.name} 文件类型不支持`);
        return false;
      }
      return false; // 阻止自动上传
    },
    onChange: (info) => {
      setFileList(info.fileList);
    },
    onRemove: (file) => {
      setFileList(fileList.filter((f) => f.uid !== file.uid));
    },
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <Card>
        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={2}>创建新项目</Title>
            <Text type="secondary">
              创建项目并上传相关资料，AI 将帮助你构建项目知识库
            </Text>
          </div>

          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateProject}
          >
            <Form.Item
              label="项目名称"
              name="name"
              rules={[{ required: true, message: '请输入项目名称' }]}
            >
              <Input placeholder="例如：XX CMS系统" size="large" />
            </Form.Item>

            <Form.Item
              label="项目描述"
              name="description"
            >
              <Input.TextArea
                placeholder="简要描述项目（选填）"
                rows={3}
              />
            </Form.Item>

            <Form.Item label="上传项目资料（选填）">
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持 PDF、Word、PowerPoint、Markdown、图片等格式，单个文件不超过 200MB
                </p>
              </Dragger>
            </Form.Item>

            {/* 文件列表 - 未开始处理时 */}
            {fileList.length > 0 && !processing && filesWithStatus.length === 0 && (
              <>
                {/* 批量操作按钮 */}
                <div style={{ marginBottom: '16px' }}>
                  <Space wrap>
                    <Button
                      size="small"
                      onClick={() => {
                        if (selectedFileIds.length === fileList.length) {
                          setSelectedFileIds([]);
                        } else {
                          setSelectedFileIds(fileList.map(f => f.uid));
                        }
                      }}
                    >
                      {selectedFileIds.length === fileList.length ? '取消全选' : '全选'}
                      ({selectedFileIds.length}/{fileList.length})
                    </Button>
                    {selectedFileIds.length > 0 && (
                      <Button
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={handleBatchDelete}
                      >
                        删除选中 ({selectedFileIds.length})
                      </Button>
                    )}
                  </Space>
                </div>

                <Card size="small" title="已选择的文件">
                  <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                    {fileList.map((file, index) => (
                      <div
                        key={file.uid}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '8px',
                          background: selectedFileIds.includes(file.uid) ? '#e6f7ff' : 'transparent',
                          borderRadius: '4px',
                          border: selectedFileIds.includes(file.uid) ? '1px solid #91d5ff' : '1px solid transparent',
                        }}
                      >
                        <Space>
                          <input
                            type="checkbox"
                            checked={selectedFileIds.includes(file.uid)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedFileIds([...selectedFileIds, file.uid]);
                              } else {
                                setSelectedFileIds(selectedFileIds.filter(id => id !== file.uid));
                              }
                            }}
                          />
                          <FileOutlined />
                          <Text>{file.name}</Text>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            ({(file.size! / 1024).toFixed(1)} KB)
                          </Text>
                        </Space>
                        <Space>
                          <Button
                            type="text"
                            size="small"
                            icon={<EyeOutlined />}
                            onClick={() => handlePreview(file)}
                          >
                            预览
                          </Button>
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => uploadProps.onRemove?.(file)}
                          />
                        </Space>
                      </div>
                    ))}
                  </Space>
                </Card>
              </>
            )}

            {/* 文件分析进度 - 处理中 */}
            {processing && filesWithStatus.length > 0 && (
              <Card size="small" title="文件分析进度">
                <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                  {filesWithStatus.map((fileStatus, index) => (
                    <div
                      key={fileStatus.file.uid}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px',
                        background: '#fafafa',
                        borderRadius: '4px',
                      }}
                    >
                      <Space>
                        <FileOutlined />
                        <Text ellipsis style={{ maxWidth: '300px' }}>
                          {fileStatus.file.name}
                        </Text>
                      </Space>
                      <Space>
                        {fileStatus.status === 'pending' && (
                          <Tag>等待中</Tag>
                        )}
                        {fileStatus.status === 'uploading' && (
                          <>
                            <Spin size="small" />
                            <Tag color="blue">上传中</Tag>
                          </>
                        )}
                        {fileStatus.status === 'analyzing' && (
                          <>
                            <Spin size="small" />
                            <Tag color="processing">分析中</Tag>
                          </>
                        )}
                        {fileStatus.status === 'completed' && (
                          <>
                            <CheckCircleOutlined style={{ color: '#52c41a' }} />
                            <Tag color="success">已完成</Tag>
                          </>
                        )}
                        {fileStatus.status === 'failed' && (
                          <Tag color="error">{fileStatus.error || '失败'}</Tag>
                        )}
                      </Space>
                    </div>
                  ))}

                  {/* 构建知识库进度 */}
                  {buildingKB && (
                    <div
                      style={{
                        marginTop: '16px',
                        padding: '12px',
                        background: '#e6f7ff',
                        borderRadius: '4px',
                      }}
                    >
                      <Space>
                        <Spin />
                        <Text strong>正在构建项目知识库...</Text>
                      </Space>
                      <Progress
                        percent={100}
                        status="active"
                        showInfo={false}
                        style={{ marginTop: '8px' }}
                      />
                    </div>
                  )}
                </Space>
              </Card>
            )}

            <Form.Item style={{ marginTop: '24px' }}>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={processing}
                >
                  {fileList.length > 0 ? '创建并分析' : '创建项目'}
                </Button>
                <Button
                  size="large"
                  onClick={() => navigate('/')}
                  disabled={processing}
                >
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Space>
      </Card>

      {/* 文件预览模态框 */}
      {previewFile && (
        <FilePreview
          visible={true}
          file={previewFile}
          onClose={() => setPreviewFile(null)}
        />
      )}
    </div>
  );
};

export default NewProject;

