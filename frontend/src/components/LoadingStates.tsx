import { Spin, Progress, Typography, Space, Card } from 'antd';
import { LoadingOutlined, RobotOutlined, FileSearchOutlined, DatabaseOutlined } from '@ant-design/icons';
import './LoadingStates.css';

const { Text } = Typography;

/**
 * AI 思考动画组件
 */
interface AIThinkingProps {
  message?: string;
  size?: 'small' | 'default' | 'large';
}

export const AIThinking = ({ message = '正在思考', size = 'default' }: AIThinkingProps) => {
  return (
    <div className={`ai-thinking ai-thinking-${size}`}>
      <div className="ai-thinking-container">
        <div className="ai-thinking-icon">
          <RobotOutlined />
        </div>
        <div className="ai-thinking-content">
          <div className="ai-thinking-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <Text type="secondary" className="ai-thinking-text">{message}</Text>
        </div>
      </div>
    </div>
  );
};

/**
 * 文件分析进度组件
 */
interface FileAnalysisProgressProps {
  fileName: string;
  status: 'uploading' | 'analyzing' | 'completed' | 'failed';
  progress?: number;
  estimatedTime?: number; // 秒
}

export const FileAnalysisProgress = ({
  fileName,
  status,
  progress = 0,
  estimatedTime,
}: FileAnalysisProgressProps) => {
  const getStatusText = () => {
    switch (status) {
      case 'uploading':
        return '正在上传...';
      case 'analyzing':
        return '正在分析...';
      case 'completed':
        return '分析完成';
      case 'failed':
        return '分析失败';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'uploading':
        return '#1890ff';
      case 'analyzing':
        return '#722ed1';
      case 'completed':
        return '#52c41a';
      case 'failed':
        return '#ff4d4f';
    }
  };

  return (
    <div className="file-analysis-progress">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        {status !== 'completed' && status !== 'failed' && (
          <Spin size="small" indicator={<LoadingOutlined />} />
        )}
        <FileSearchOutlined style={{ fontSize: '16px', color: getStatusColor() }} />
        <Text strong ellipsis style={{ flex: 1, maxWidth: '300px' }}>
          {fileName}
        </Text>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          {getStatusText()}
        </Text>
      </div>
      <Progress
        percent={progress}
        strokeColor={getStatusColor()}
        status={status === 'failed' ? 'exception' : status === 'completed' ? 'success' : 'active'}
        showInfo={false}
        size="small"
      />
      {estimatedTime && status !== 'completed' && status !== 'failed' && (
        <Text type="secondary" style={{ fontSize: '11px', marginTop: '4px', display: 'block' }}>
          预计还需 {estimatedTime} 秒
        </Text>
      )}
    </div>
  );
};

/**
 * 知识库构建进度组件
 */
interface KnowledgeBaseProgressProps {
  stage: 'analyzing_files' | 'extracting_info' | 'building_structure' | 'completing';
  filesProcessed?: number;
  totalFiles?: number;
  estimatedTime?: number;
}

export const KnowledgeBaseProgress = ({
  stage,
  filesProcessed = 0,
  totalFiles = 0,
  estimatedTime,
}: KnowledgeBaseProgressProps) => {
  const stageInfo = {
    analyzing_files: {
      title: '分析文件',
      description: '正在分析上传的文件内容...',
      icon: <FileSearchOutlined />,
      progress: 25,
    },
    extracting_info: {
      title: '提取信息',
      description: 'AI 正在提取关键信息和结构化数据...',
      icon: <RobotOutlined />,
      progress: 50,
    },
    building_structure: {
      title: '构建知识库',
      description: '正在整合信息，构建项目知识库...',
      icon: <DatabaseOutlined />,
      progress: 75,
    },
    completing: {
      title: '完成',
      description: '知识库构建即将完成...',
      icon: <DatabaseOutlined />,
      progress: 95,
    },
  };

  const currentStage = stageInfo[stage];

  return (
    <Card size="small" className="kb-progress">
      <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
          <div style={{ flex: 1 }}>
            <Text strong style={{ fontSize: '15px' }}>
              {currentStage.title}
            </Text>
            <Text type="secondary" style={{ display: 'block', fontSize: '12px', marginTop: '4px' }}>
              {currentStage.description}
            </Text>
          </div>
          <div style={{ fontSize: '24px', color: '#1890ff' }}>
            {currentStage.icon}
          </div>
        </div>

        <div>
          <Progress
            percent={currentStage.progress}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
            status="active"
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
            {totalFiles > 0 && (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                已处理 {filesProcessed}/{totalFiles} 个文件
              </Text>
            )}
            {estimatedTime && (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                预计还需 {Math.ceil(estimatedTime / 60)} 分钟
              </Text>
            )}
          </div>
        </div>

        <div className="kb-progress-stages">
          <Space size="small">
            {Object.keys(stageInfo).map((key) => {
              const s = stageInfo[key as keyof typeof stageInfo];
              const isCompleted = s.progress <= currentStage.progress;
              const isCurrent = key === stage;

              return (
                <div
                  key={key}
                  className={`kb-progress-stage ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
                >
                  <div className="kb-progress-stage-dot" />
                  <Text
                    type={isCompleted ? 'success' : 'secondary'}
                    style={{ fontSize: '11px' }}
                  >
                    {s.title}
                  </Text>
                </div>
              );
            })}
          </Space>
        </div>
      </Space>
    </Card>
  );
};

/**
 * 全屏加载遮罩
 */
interface FullPageLoadingProps {
  message?: string;
  tip?: string;
}

export const FullPageLoading = ({
  message = '正在处理',
  tip = '请稍候...',
}: FullPageLoadingProps) => {
  return (
    <div className="full-page-loading">
      <div className="full-page-loading-content">
        <Spin size="large" tip={message} />
        <Text type="secondary" style={{ marginTop: '16px', display: 'block' }}>
          {tip}
        </Text>
      </div>
    </div>
  );
};
