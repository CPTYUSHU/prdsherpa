import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Space, message, Spin, Select, Modal, Card, Image, Checkbox } from 'antd';
import {
  DownloadOutlined,
  ArrowLeftOutlined,
  PictureOutlined,
  MobileOutlined,
  TabletOutlined,
  DesktopOutlined,
  FileImageOutlined,
} from '@ant-design/icons';
import { wireframeApi, filesApi } from '../services/api';
import DOMPurify from 'dompurify';
import html2canvas from 'html2canvas';
import { UploadedFile } from '../types';

const WireframePreview = () => {
  const { projectId, conversationId } = useParams<{ projectId: string; conversationId: string }>();
  const navigate = useNavigate();
  const [htmlContent, setHtmlContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [deviceType, setDeviceType] = useState<'mobile' | 'tablet' | 'desktop'>('mobile');
  const [exporting, setExporting] = useState(false);
  const [referenceFileIds, setReferenceFileIds] = useState<string[]>([]);
  const [showReferenceModal, setShowReferenceModal] = useState(false);
  const [availableFiles, setAvailableFiles] = useState<UploadedFile[]>([]);

  useEffect(() => {
    if (projectId) {
      loadAvailableFiles();
    }
  }, [projectId]);

  useEffect(() => {
    if (conversationId) {
      loadWireframe();
    }
  }, [conversationId, deviceType, referenceFileIds]);

  const loadAvailableFiles = async () => {
    if (!projectId) return;
    try {
      const files = await filesApi.list(projectId);
      // 只显示图片文件
      const imageFiles = files.filter((f: UploadedFile) => f.file_type === 'image');
      setAvailableFiles(imageFiles);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const loadWireframe = async () => {
    if (!conversationId) return;
    try {
      setLoading(true);
      const data = await wireframeApi.generate(conversationId, deviceType, referenceFileIds);

      // 使用 DOMPurify 清理 HTML，防止 XSS 攻击
      const cleanHtml = DOMPurify.sanitize(data.html_content, {
        ALLOWED_TAGS: [
          'html', 'head', 'body', 'title', 'meta', 'style', 'script',
          'div', 'span', 'p', 'a', 'button', 'input', 'textarea',
          'label', 'ul', 'ol', 'li', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
          'table', 'thead', 'tbody', 'tr', 'td', 'th', 'br', 'hr',
          'strong', 'em', 'b', 'i', 'u', 'small', 'code', 'pre'
        ],
        ALLOWED_ATTR: [
          'class', 'id', 'style', 'type', 'placeholder', 'href', 'src',
          'onclick', 'width', 'height', 'alt', 'title', 'lang', 'charset',
          'name', 'content', 'rel', 'target'
        ],
        ALLOW_DATA_ATTR: false,
      });

      setHtmlContent(cleanHtml);
      message.success('线框图生成成功！');
    } catch (error: any) {
      console.error('Failed to generate wireframe:', error);
      const errorMsg = error.response?.data?.detail || '生成线框图失败';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadHTML = () => {
    try {
      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `wireframe_${deviceType}_${Date.now()}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      message.success('HTML 文件已下载');
    } catch (error) {
      console.error('Download error:', error);
      message.error('下载失败');
    }
  };

  const handleExportImage = async () => {
    try {
      setExporting(true);
      const iframe = document.getElementById('wireframe-iframe') as HTMLIFrameElement;
      if (!iframe?.contentWindow?.document.body) {
        message.error('无法获取线框图内容');
        return;
      }

      // 使用 html2canvas 截图
      const canvas = await html2canvas(iframe.contentWindow.document.body, {
        backgroundColor: '#ffffff',
        scale: 2, // 提高分辨率
        logging: false,
      });

      // 转换为 Blob 并下载
      canvas.toBlob((blob) => {
        if (!blob) {
          message.error('导出失败');
          return;
        }
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `wireframe_${deviceType}_${Date.now()}.png`;
        a.click();
        window.URL.revokeObjectURL(url);
        message.success('图片已导出');
      });
    } catch (error) {
      console.error('Export error:', error);
      message.error('导出图片失败');
    } finally {
      setExporting(false);
    }
  };

  const handleRegenerate = () => {
    loadWireframe();
  };

  const deviceIcons = {
    mobile: <MobileOutlined />,
    tablet: <TabletOutlined />,
    desktop: <DesktopOutlined />,
  };

  if (loading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f5f5f5'
      }}>
        <Spin size="large" />
        <p style={{ marginTop: '24px', fontSize: '16px', color: '#666' }}>
          AI 正在生成 {deviceType === 'mobile' ? '移动端' : deviceType === 'tablet' ? '平板' : '桌面端'} 线框图...
        </p>
        <p style={{ marginTop: '8px', fontSize: '14px', color: '#999' }}>
          这可能需要 20-30 秒，请耐心等待
        </p>
      </div>
    );
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#f5f5f5' }}>
      {/* 工具栏 */}
      <div style={{
        padding: '16px 24px',
        borderBottom: '1px solid #e8e8e8',
        background: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
      }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(`/project/${projectId}/chat/${conversationId}`)}
            >
              返回对话
            </Button>

            {/* 设备类型选择 */}
            <Select
              value={deviceType}
              onChange={(value) => setDeviceType(value)}
              style={{ width: 120 }}
              suffixIcon={deviceIcons[deviceType]}
            >
              <Select.Option value="mobile">
                <Space>
                  <MobileOutlined />
                  移动端
                </Space>
              </Select.Option>
              <Select.Option value="tablet">
                <Space>
                  <TabletOutlined />
                  平板
                </Space>
              </Select.Option>
              <Select.Option value="desktop">
                <Space>
                  <DesktopOutlined />
                  桌面端
                </Space>
              </Select.Option>
            </Select>

            <Button
              onClick={() => setShowReferenceModal(true)}
              icon={<FileImageOutlined />}
            >
              参考截图 {referenceFileIds.length > 0 && `(${referenceFileIds.length})`}
            </Button>

            <Button onClick={handleRegenerate}>
              重新生成
            </Button>
          </Space>

          <Space>
            <Button onClick={handleDownloadHTML} icon={<DownloadOutlined />}>
              下载 HTML
            </Button>
            <Button
              onClick={handleExportImage}
              type="primary"
              icon={<PictureOutlined />}
              loading={exporting}
            >
              导出图片
            </Button>
          </Space>
        </Space>
      </div>

      {/* 线框图预览区 */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        padding: '40px',
      }}>
        {htmlContent ? (
          <div style={{
            maxWidth: '100%',
            margin: '0 auto',
            background: '#fff',
            boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
            borderRadius: '8px',
            overflow: 'hidden'
          }}>
            {/* 使用 iframe 隔离渲染，更安全 */}
            <iframe
              id="wireframe-iframe"
              srcDoc={htmlContent}
              style={{
                width: '100%',
                minHeight: '800px',
                border: 'none',
                display: 'block'
              }}
              sandbox="allow-same-origin allow-scripts"
              title="Wireframe Preview"
            />
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '100px 20px',
            color: '#999'
          }}>
            <p>暂无线框图内容</p>
          </div>
        )}
      </div>

      {/* 提示信息 */}
      {htmlContent && (
        <div style={{
          padding: '12px 24px',
          background: referenceFileIds.length > 0 ? '#e6f7ff' : '#fff9e6',
          borderTop: `1px solid ${referenceFileIds.length > 0 ? '#91d5ff' : '#ffe58f'}`,
          textAlign: 'center',
          fontSize: '12px',
          color: '#666'
        }}>
          {referenceFileIds.length > 0 ? (
            <>
              🎨 已使用 {referenceFileIds.length} 个参考截图生成高保真原型，保留了现有界面的设计风格
            </>
          ) : (
            <>
              💡 提示：这是低保真线框图原型，仅用于展示功能布局和交互流程，不代表最终设计效果
              <br />
              建议上传现有系统截图作为参考，生成更高保真的原型
            </>
          )}
        </div>
      )}

      {/* 参考截图选择模态框 */}
      <Modal
        title="选择参考截图"
        open={showReferenceModal}
        onCancel={() => setShowReferenceModal(false)}
        onOk={() => {
          setShowReferenceModal(false);
          message.success(`已选择 ${referenceFileIds.length} 个参考截图`);
        }}
        width={800}
        okText="确定"
        cancelText="取消"
      >
        <div style={{ marginBottom: '16px', padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
            💡 <strong>选择参考截图的作用：</strong>
          </p>
          <ul style={{ margin: '8px 0 0', paddingLeft: '20px', fontSize: '12px', color: '#666' }}>
            <li>AI 会分析参考截图的布局结构、组件样式和配色方案</li>
            <li>生成的原型会模仿参考截图的设计风格，保持视觉一致性</li>
            <li>明确标注新功能应该添加在界面的哪个位置</li>
            <li>帮助开发人员快速定位功能开发的位置，减少理解成本</li>
          </ul>
        </div>

        {availableFiles.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
            <FileImageOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <p>暂无可用的图片文件</p>
            <p style={{ fontSize: '12px' }}>
              请先在项目中上传现有系统的截图（PNG、JPG 等格式）
            </p>
          </div>
        ) : (
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <Checkbox.Group
              value={referenceFileIds}
              onChange={(values) => setReferenceFileIds(values as string[])}
              style={{ width: '100%' }}
            >
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: '16px'
              }}>
                {availableFiles.map((file) => (
                  <Card
                    key={file.id}
                    hoverable
                    cover={
                      <div style={{ height: '150px', overflow: 'hidden', background: '#f5f5f5' }}>
                        <Image
                          src={`http://localhost:8000/${file.file_path}`}
                          alt={file.original_filename}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          preview={true}
                        />
                      </div>
                    }
                    bodyStyle={{ padding: '12px' }}
                  >
                    <Checkbox value={file.id} style={{ width: '100%' }}>
                      <div style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontSize: '12px'
                      }}>
                        {file.original_filename}
                      </div>
                    </Checkbox>
                  </Card>
                ))}
              </div>
            </Checkbox.Group>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default WireframePreview;
