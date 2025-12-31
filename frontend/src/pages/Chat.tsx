import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Input,
  Button,
  Space,
  Typography,
  Spin,
  message,
  Modal,
  Card,
  Tabs,
  Tooltip,
} from 'antd';
import {
  SendOutlined,
  DownloadOutlined,
  UserOutlined,
  RobotOutlined,
  BookOutlined,
  ArrowLeftOutlined,
  MessageOutlined,
  FileTextOutlined,
  CopyOutlined,
  ReloadOutlined,
  EditOutlined,
  LoadingOutlined,
  LayoutOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { conversationApi, exportApi, fileApi } from '../services/api';
import type { Message, ConversationDetail } from '../types';
import PRDPreview from '../components/PRDPreview';
import { AIThinking } from '../components/LoadingStates';
import { useApiError } from '../hooks/useApiError';

const { TextArea } = Input;
const { Text } = Typography;

const Chat = () => {
  const navigate = useNavigate();
  const { projectId, conversationId } = useParams<{ projectId: string; conversationId?: string }>();
  const { handleUploadError, handleTimeout, showDetailedError } = useApiError();
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [exportContent, setExportContent] = useState('');
  const [pastedImages, setPastedImages] = useState<File[]>([]);
  const [thinkingStatus, setThinkingStatus] = useState<string>('');
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textAreaRef = useRef<any>(null);

  useEffect(() => {
    if (conversationId) {
      loadConversation();
    } else if (projectId) {
      // 如果没有 conversationId，导航到需求列表
      navigate(`/project/${projectId}`);
    }
  }, [conversationId, projectId, navigate]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 处理粘贴事件
  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    const imageFiles: File[] = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf('image') !== -1) {
        e.preventDefault(); // 阻止默认粘贴行为
        const file = item.getAsFile();
        if (file) {
          imageFiles.push(file);
        }
      }
    }

    if (imageFiles.length > 0) {
      setPastedImages([...pastedImages, ...imageFiles]);
      message.success(`已粘贴 ${imageFiles.length} 张图片`);
    }
  };

  // 移除粘贴的图片
  const handleRemoveImage = (index: number) => {
    const newImages = [...pastedImages];
    newImages.splice(index, 1);
    setPastedImages(newImages);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };


  const loadConversation = async () => {
    if (!conversationId) return;
    try {
      setLoading(true);
      const data = await conversationApi.get(conversationId);
      setConversation(data);
      setMessages(data.messages || []);
    } catch (error: any) {
      console.error('Failed to load conversation:', error);
      message.error('加载对话失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!conversation || (!inputValue.trim() && pastedImages.length === 0)) return;

    const userMessage = inputValue.trim();
    const imagesToUpload = [...pastedImages];
    setInputValue('');
    setPastedImages([]);
    setSending(true);

    try {
      let uploadedFileIds: string[] = [];

      // 如果有图片，先上传到项目
      if (imagesToUpload.length > 0 && projectId) {
        setThinkingStatus(`正在上传 ${imagesToUpload.length} 张图片...`);

        try {
          for (let i = 0; i < imagesToUpload.length; i++) {
            const imageFile = imagesToUpload[i];
            // 上传文件
            const uploadedFile = await fileApi.upload(projectId, imageFile);
            uploadedFileIds.push(uploadedFile.id);

            // 更新进度提示
            setThinkingStatus(`已上传 ${i + 1}/${imagesToUpload.length} 张图片...`);
          }

          setThinkingStatus('图片上传完成，AI 正在分析...');
        } catch (uploadError: any) {
          setThinkingStatus('');
          message.error('图片上传失败');
          console.error('Upload error:', uploadError);
          throw uploadError; // 上传失败就不继续了
        }
      }

      // 发送消息（包含图片文件 ID）
      let finalMessage = userMessage;
      if (imagesToUpload.length > 0) {
        finalMessage = userMessage || `请分析这 ${imagesToUpload.length} 张图片并总结关键信息`;
      }

      // 显示 AI 思考过程
      setThinkingStatus('正在生成回复...');

      // 使用流式 API
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const url = `${API_BASE_URL}/api/conversations/${conversation.id}/chat-stream`;

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: finalMessage,
          image_file_ids: uploadedFileIds.length > 0 ? uploadedFileIds : undefined,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let userMsg: Message | null = null;
      let aiMsg: Message | null = null;
      let aiContent = '';
      let currentEventType = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEventType = line.substring(6).trim();
            continue;
          }

          if (line.startsWith('data:')) {
            const data = line.substring(5).trim();
            if (!data) continue;

            try {
              const parsed = JSON.parse(data);

              // 根据当前事件类型处理数据
              if (currentEventType === 'user_message') {
                userMsg = parsed as Message;
                // 立即显示用户消息
                setMessages((prev) => [...prev, userMsg!]);
              } else if (currentEventType === 'chunk') {
                // 流式更新 AI 回复
                aiContent += parsed.text;
                // 创建临时消息对象用于显示
                if (!aiMsg) {
                  aiMsg = {
                    id: 'temp-' + Date.now(),
                    conversation_id: conversation.id,
                    role: 'assistant',
                    content: aiContent,
                    sequence: (userMsg?.sequence || 0) + 1,
                    created_at: new Date().toISOString(),
                  } as Message;
                  setMessages((prev) => [...prev, aiMsg!]);
                } else {
                  // 更新现有消息
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === aiMsg!.id ? { ...msg, content: aiContent } : msg
                    )
                  );
                }
              } else if (currentEventType === 'assistant_message') {
                // 用完整的服务器消息替换临时消息
                aiMsg = parsed as Message;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.role === 'assistant' && msg.id.toString().startsWith('temp-')
                      ? aiMsg!
                      : msg
                  )
                );
              } else if (currentEventType === 'done') {
                setThinkingStatus('');
              } else if (currentEventType === 'error') {
                throw new Error(parsed.error);
              }

              // 重置事件类型
              currentEventType = '';
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError);
            }
          }
        }
      }

      setThinkingStatus('');
    } catch (error: any) {
      console.error('Failed to send message:', error);
      const errorMsg = error.code === 'ECONNABORTED'
        ? 'AI 处理超时，请稍后重试或减少图片数量'
        : '发送失败';
      message.error(errorMsg);
      setInputValue(userMessage);
      setPastedImages(imagesToUpload);
      setThinkingStatus('');
    } finally {
      setSending(false);
    }
  };

  const handleExport = async () => {
    if (!conversation) return;
    try {
      setExporting(true);
      const result = await exportApi.export(conversation.id);
      setExportContent(result.content);
      setExportModalVisible(true);
    } catch (error: any) {
      console.error('Failed to export:', error);
      message.error('导出失败');
    } finally {
      setExporting(false);
    }
  };

  const handleGenerateWireframe = () => {
    if (!conversationId || !projectId) return;
    // 直接跳转到线框图预览页面，由预览页面负责调用 API 生成
    navigate(`/project/${projectId}/wireframe/${conversationId}`);
  };

  const handleDownload = async () => {
    if (!conversation) return;
    try {
      const blob = await exportApi.download(conversation.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PRD_${conversation.title}_${new Date().getTime()}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      message.success('下载成功！');
      setExportModalVisible(false);
    } catch (error: any) {
      console.error('Failed to download:', error);
      message.error('下载失败');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSend();
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
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 添加消息悬停时显示操作按钮的样式 */}
      <style>
        {`
          .message-container:hover .message-actions {
            opacity: 1 !important;
          }
        `}
      </style>

      {/* 顶部工具栏 */}
      <div style={{
        padding: '16px 24px',
        borderBottom: '1px solid #f0f0f0',
        background: '#fff',
      }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(`/project/${projectId}`)}
            >
              返回需求列表
            </Button>
            <Text strong style={{ fontSize: '16px' }}>
              {conversation?.title || '新对话'}
            </Text>
          </Space>
          <Space>
            <Button
              icon={<BookOutlined />}
              onClick={() => navigate(`/project/${projectId}/knowledge`)}
            >
              查看知识库
            </Button>
            <Button
              icon={<LayoutOutlined />}
              onClick={handleGenerateWireframe}
              disabled={messages.length === 0}
            >
              生成线框图
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
              loading={exporting}
              disabled={messages.length === 0}
            >
              导出 PRD
            </Button>
          </Space>
        </Space>
      </div>

      {/* 主内容区 - 使用 Tabs 切换对话和 PRD 预览 */}
      <div style={{ flex: 1, overflow: 'hidden', background: '#fff' }}>
        <Tabs
          defaultActiveKey="chat"
          style={{ height: '100%' }}
          items={[
            {
              key: 'chat',
              label: (
                <span>
                  <MessageOutlined /> 对话
                </span>
              ),
              children: (
                <div style={{
                  height: 'calc(100vh - 200px)',
                  overflow: 'auto',
                  padding: '24px',
                  background: '#fafafa',
                }}>
                  {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '60px 20px', color: '#999' }}>
                      <Text type="secondary">开始描述你的需求吧...</Text>
                    </div>
                  ) : (
                    <Space orientation="vertical" size="large" style={{ width: '100%' }}>
                      {messages.map((msg) => (
                        <div
                          key={msg.id}
                          className="message-container"
                          style={{
                            display: 'flex',
                            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                          }}
                        >
                          <div style={{
                            maxWidth: '70%',
                            display: 'flex',
                            gap: '12px',
                            flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                          }}>
                            {/* 头像 */}
                            <div style={{
                              width: '36px',
                              height: '36px',
                              borderRadius: '50%',
                              background: msg.role === 'user' ? '#1890ff' : '#52c41a',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: '#fff',
                              flexShrink: 0,
                            }}>
                              {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                            </div>

                            {/* 消息内容 */}
                            <div style={{
                              background: msg.role === 'user' ? '#1890ff' : '#fff',
                              color: msg.role === 'user' ? '#fff' : '#000',
                              padding: '12px 16px',
                              borderRadius: '8px',
                              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                              position: 'relative',
                            }}>
                              {msg.role === 'assistant' ? (
                                <>
                                  <div className="markdown-body">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                      {msg.content}
                                    </ReactMarkdown>
                                  </div>
                                  {/* 快速操作按钮 */}
                                  <div style={{
                                    position: 'absolute',
                                    top: '8px',
                                    right: '8px',
                                    display: 'flex',
                                    gap: '4px',
                                    opacity: 0,
                                    transition: 'opacity 0.2s',
                                  }}
                                  className="message-actions"
                                  >
                                    <Tooltip title="复制">
                                      <Button
                                        type="text"
                                        size="small"
                                        icon={<CopyOutlined />}
                                        onClick={() => {
                                          navigator.clipboard.writeText(msg.content);
                                          message.success('已复制到剪贴板');
                                        }}
                                      />
                                    </Tooltip>
                                    <Tooltip title="重新生成">
                                      <Button
                                        type="text"
                                        size="small"
                                        icon={<ReloadOutlined />}
                                        onClick={() => {
                                          message.info('重新生成功能开发中...');
                                        }}
                                      />
                                    </Tooltip>
                                  </div>
                                </>
                              ) : (
                                <>
                                  <Text style={{ color: '#fff', whiteSpace: 'pre-wrap' }}>
                                    {msg.content}
                                  </Text>
                                  {/* 用户消息快速操作 */}
                                  <div style={{
                                    position: 'absolute',
                                    top: '8px',
                                    right: '8px',
                                    display: 'flex',
                                    gap: '4px',
                                    opacity: 0,
                                    transition: 'opacity 0.2s',
                                  }}
                                  className="message-actions"
                                  >
                                    <Tooltip title="编辑">
                                      <Button
                                        type="text"
                                        size="small"
                                        icon={<EditOutlined style={{ color: '#fff' }} />}
                                        onClick={() => {
                                          setEditingMessageId(msg.id);
                                          setEditingContent(msg.content);
                                        }}
                                      />
                                    </Tooltip>
                                  </div>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}

                      {/* AI 思考状态显示 */}
                      {thinkingStatus && (
                        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                          <AIThinking message={thinkingStatus} />
                        </div>
                      )}

                      <div ref={messagesEndRef} />
                    </Space>
                  )}
                </div>
              ),
            },
            {
              key: 'prd',
              label: (
                <span>
                  <FileTextOutlined /> PRD 预览
                </span>
              ),
              children: (
                <div style={{
                  height: 'calc(100vh - 200px)',
                  overflow: 'auto',
                  padding: '24px',
                }}>
                  {conversationId && <PRDPreview conversationId={conversationId} />}
                </div>
              ),
            },
          ]}
        />
      </div>

      {/* 输入框 */}
      <div style={{
        padding: '16px 24px',
        borderTop: '1px solid #f0f0f0',
        background: '#fff',
      }}>
        {/* 粘贴的图片预览 */}
        {pastedImages.length > 0 && (
          <div style={{ marginBottom: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {pastedImages.map((img, index) => (
              <div key={index} style={{ position: 'relative' }}>
                <img
                  src={URL.createObjectURL(img)}
                  alt={`pasted-${index}`}
                  style={{
                    width: '80px',
                    height: '80px',
                    objectFit: 'cover',
                    borderRadius: '4px',
                    border: '1px solid #d9d9d9',
                  }}
                />
                <Button
                  type="text"
                  danger
                  size="small"
                  style={{
                    position: 'absolute',
                    top: '-8px',
                    right: '-8px',
                    background: '#fff',
                    borderRadius: '50%',
                    minWidth: '24px',
                    height: '24px',
                    padding: '0',
                  }}
                  onClick={() => handleRemoveImage(index)}
                >
                  ×
                </Button>
              </div>
            ))}
          </div>
        )}
        
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            ref={textAreaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder="描述你的需求... (支持粘贴截图，Ctrl/Cmd + Enter 发送)"
            autoSize={{ minRows: 2, maxRows: 6 }}
            disabled={sending}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={sending}
            disabled={!inputValue.trim() && pastedImages.length === 0}
            style={{ height: 'auto' }}
          >
            发送
          </Button>
        </Space.Compact>
      </div>

      {/* 编辑消息弹窗 */}
      <Modal
        title="编辑消息"
        open={editingMessageId !== null}
        onOk={async () => {
          if (!editingContent.trim() || !conversation || !editingMessageId) return;

          try {
            setSending(true);
            setEditingMessageId(null);

            // 找到被编辑的消息的索引
            const editedMsgIndex = messages.findIndex(m => m.id === editingMessageId);
            if (editedMsgIndex === -1) return;

            // 删除从编辑点开始的所有消息
            const newMessages = messages.slice(0, editedMsgIndex);
            setMessages(newMessages);

            // 显示 AI 思考过程
            setThinkingStatus('正在分析需求...');

            // 模拟思考过程的阶段变化
            const thinkingStages = [
              { delay: 800, text: '正在查询知识库...' },
              { delay: 1200, text: '正在生成回复...' },
            ];

            const timers: NodeJS.Timeout[] = [];
            thinkingStages.forEach(stage => {
              const timer = setTimeout(() => {
                setThinkingStatus(stage.text);
              }, stage.delay);
              timers.push(timer);
            });

            // 发送编辑后的消息
            const response = await conversationApi.chat(conversation.id, editingContent);

            // 清除所有计时器
            timers.forEach(timer => clearTimeout(timer));

            setMessages([...newMessages, response.user_message, response.assistant_message]);
            setThinkingStatus('');
            message.success('消息已重新发送');
          } catch (error: any) {
            console.error('Failed to resend message:', error);
            message.error('重新发送失败');
            setThinkingStatus('');
          } finally {
            setSending(false);
          }
        }}
        onCancel={() => {
          setEditingMessageId(null);
          setEditingContent('');
        }}
        confirmLoading={sending}
        width={600}
      >
        <TextArea
          value={editingContent}
          onChange={(e) => setEditingContent(e.target.value)}
          autoSize={{ minRows: 4, maxRows: 12 }}
          placeholder="修改你的消息..."
        />
        <div style={{ marginTop: '8px', color: '#999', fontSize: '12px' }}>
          💡 编辑后将删除此消息之后的所有对话，并重新生成 AI 回复
        </div>
      </Modal>

      {/* 导出预览弹窗 */}
      <Modal
        title="PRD 预览"
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setExportModalVisible(false)}>
            取消
          </Button>,
          <Button key="download" type="primary" icon={<DownloadOutlined />} onClick={handleDownload}>
            下载 MD 文件
          </Button>,
        ]}
      >
        <Card style={{ maxHeight: '60vh', overflow: 'auto' }}>
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {exportContent}
            </ReactMarkdown>
          </div>
        </Card>
      </Modal>
    </div>
  );
};

export default Chat;

