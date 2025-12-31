import { useState } from 'react';
import { Modal, Spin, Image, Typography, Button, Space, message } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  RotateLeftOutlined,
  RotateRightOutlined,
  DownloadOutlined,
  CloseOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FilePptOutlined,
  FileUnknownOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { UploadedFile } from '../../types';
import './FilePreview.css';

const { Text, Title } = Typography;

interface FilePreviewProps {
  file: UploadedFile | null;
  visible: boolean;
  onClose: () => void;
}

/**
 * 文件预览组件
 * 支持 PDF、图片、Markdown、文本等多种格式
 */
const FilePreview = ({ file, visible, onClose }: FilePreviewProps) => {
  const [loading, setLoading] = useState(false);
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [markdownContent, setMarkdownContent] = useState('');
  const [textContent, setTextContent] = useState('');

  if (!file) return null;

  // 获取文件类型
  const getFileType = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'];
    const docExts = ['doc', 'docx'];
    const excelExts = ['xls', 'xlsx'];
    const pptExts = ['ppt', 'pptx'];
    const markdownExts = ['md', 'markdown'];
    const textExts = ['txt', 'log', 'json', 'xml', 'csv'];

    if (ext === 'pdf') return 'pdf';
    if (imageExts.includes(ext)) return 'image';
    if (markdownExts.includes(ext)) return 'markdown';
    if (textExts.includes(ext)) return 'text';
    if (docExts.includes(ext)) return 'word';
    if (excelExts.includes(ext)) return 'excel';
    if (pptExts.includes(ext)) return 'ppt';

    return 'unknown';
  };

  const fileType = getFileType(file.filename);

  // 获取文件图标
  const getFileIcon = () => {
    const iconProps = { style: { fontSize: '48px' } };

    switch (fileType) {
      case 'pdf':
        return <FilePdfOutlined {...iconProps} style={{ ...iconProps.style, color: '#ff4d4f' }} />;
      case 'image':
        return <FileImageOutlined {...iconProps} style={{ ...iconProps.style, color: '#52c41a' }} />;
      case 'markdown':
      case 'text':
        return <FileTextOutlined {...iconProps} style={{ ...iconProps.style, color: '#1890ff' }} />;
      case 'word':
        return <FileWordOutlined {...iconProps} style={{ ...iconProps.style, color: '#1890ff' }} />;
      case 'excel':
        return <FileExcelOutlined {...iconProps} style={{ ...iconProps.style, color: '#52c41a' }} />;
      case 'ppt':
        return <FilePptOutlined {...iconProps} style={{ ...iconProps.style, color: '#ff4d4f' }} />;
      default:
        return <FileUnknownOutlined {...iconProps} style={{ ...iconProps.style, color: '#8c8c8c' }} />;
    }
  };

  // 获取文件 URL
  const getFileUrl = () => {
    // 实际项目中这里应该是从后端获取的完整 URL
    return `http://localhost:8000${file.file_path}`;
  };

  // 下载文件
  const handleDownload = () => {
    const url = getFileUrl();
    const link = document.createElement('a');
    link.href = url;
    link.download = file.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('下载已开始');
  };

  // 渲染 PDF 预览
  const renderPDFPreview = () => {
    return (
      <div className="file-preview-pdf">
        <div className="pdf-viewer">
          {/* PDF.js 集成 */}
          <iframe
            src={`${getFileUrl()}#toolbar=0`}
            width="100%"
            height="600px"
            style={{ border: 'none' }}
            title={file.filename}
          />
        </div>
        <Text type="secondary" style={{ display: 'block', marginTop: '16px', textAlign: 'center' }}>
          PDF 文件预览 - {file.filename}
        </Text>
      </div>
    );
  };

  // 渲染图片预览
  const renderImagePreview = () => {
    return (
      <div className="file-preview-image">
        <div
          className="image-container"
          style={{
            transform: `scale(${scale}) rotate(${rotation}deg)`,
            transition: 'transform 0.3s ease',
          }}
        >
          <Image
            src={getFileUrl()}
            alt={file.filename}
            preview={false}
            style={{ maxWidth: '100%', maxHeight: '600px' }}
          />
        </div>

        {/* 图片控制按钮 */}
        <div className="image-controls">
          <Space>
            <Button
              icon={<ZoomOutOutlined />}
              onClick={() => setScale(Math.max(0.5, scale - 0.25))}
              disabled={scale <= 0.5}
            >
              缩小
            </Button>
            <Button onClick={() => setScale(1)}>重置</Button>
            <Button
              icon={<ZoomInOutlined />}
              onClick={() => setScale(Math.min(3, scale + 0.25))}
              disabled={scale >= 3}
            >
              放大
            </Button>
            <Button
              icon={<RotateLeftOutlined />}
              onClick={() => setRotation(rotation - 90)}
            >
              左转
            </Button>
            <Button
              icon={<RotateRightOutlined />}
              onClick={() => setRotation(rotation + 90)}
            >
              右转
            </Button>
          </Space>
        </div>
      </div>
    );
  };

  // 渲染 Markdown 预览
  const renderMarkdownPreview = () => {
    return (
      <div className="file-preview-markdown">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {file.analysis_result?.summary || '# Markdown 文件\n\n无内容'}
        </ReactMarkdown>
      </div>
    );
  };

  // 渲染文本预览
  const renderTextPreview = () => {
    return (
      <div className="file-preview-text">
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {file.analysis_result?.summary || '文本内容'}
        </pre>
      </div>
    );
  };

  // 渲染不支持的文件类型
  const renderUnsupportedPreview = () => {
    return (
      <div className="file-preview-unsupported">
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          {getFileIcon()}
          <Title level={4} style={{ marginTop: '24px' }}>
            {file.filename}
          </Title>
          <Text type="secondary">
            该文件类型暂不支持在线预览
          </Text>
          <div style={{ marginTop: '24px' }}>
            <Button type="primary" icon={<DownloadOutlined />} onClick={handleDownload}>
              下载文件
            </Button>
          </div>

          {/* 显示文件分析结果 */}
          {file.analysis_result && (
            <div style={{ marginTop: '32px', textAlign: 'left', maxWidth: '600px', margin: '32px auto' }}>
              <Title level={5}>AI 分析结果</Title>
              {file.analysis_result.summary && (
                <div style={{ marginTop: '16px' }}>
                  <Text strong>内容摘要：</Text>
                  <Text>{file.analysis_result.summary}</Text>
                </div>
              )}
              {file.analysis_result.entities && file.analysis_result.entities.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <Text strong>关键实体：</Text>
                  <div style={{ marginTop: '8px' }}>
                    {file.analysis_result.entities.slice(0, 10).map((entity: string, idx: number) => (
                      <span
                        key={idx}
                        style={{
                          display: 'inline-block',
                          padding: '4px 12px',
                          margin: '4px',
                          background: '#f0f0f0',
                          borderRadius: '4px',
                        }}
                      >
                        {entity}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  // 渲染预览内容
  const renderPreviewContent = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" tip="加载中..." />
        </div>
      );
    }

    switch (fileType) {
      case 'pdf':
        return renderPDFPreview();
      case 'image':
        return renderImagePreview();
      case 'markdown':
        return renderMarkdownPreview();
      case 'text':
        return renderTextPreview();
      default:
        return renderUnsupportedPreview();
    }
  };

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      width={fileType === 'pdf' || fileType === 'image' ? 900 : 800}
      footer={[
        <Button key="download" icon={<DownloadOutlined />} onClick={handleDownload}>
          下载文件
        </Button>,
        <Button key="close" type="primary" icon={<CloseOutlined />} onClick={onClose}>
          关闭
        </Button>,
      ]}
      title={
        <Space>
          {getFileIcon()}
          <div>
            <div>{file.filename}</div>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              大小: {(file.file_size / 1024 / 1024).toFixed(2)} MB | 类型: {file.file_type}
            </Text>
          </div>
        </Space>
      }
      className="file-preview-modal"
      destroyOnClose
    >
      <div className="file-preview-content">
        {renderPreviewContent()}
      </div>
    </Modal>
  );
};

export default FilePreview;
