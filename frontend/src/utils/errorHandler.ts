import { message, Modal, notification } from 'antd';

/**
 * 错误类型定义
 */
export enum ErrorType {
  NETWORK = 'network',
  TIMEOUT = 'timeout',
  UPLOAD = 'upload',
  AI_ANALYSIS = 'ai_analysis',
  VALIDATION = 'validation',
  UNKNOWN = 'unknown',
}

/**
 * 错误信息接口
 */
export interface ErrorInfo {
  type: ErrorType;
  message: string;
  details?: string;
  retryable?: boolean;
  onRetry?: () => void | Promise<void>;
}

/**
 * 解析 API 错误
 */
export const parseApiError = (error: any): ErrorInfo => {
  // 网络错误
  if (!error.response && error.request) {
    return {
      type: ErrorType.NETWORK,
      message: '网络连接失败',
      details: '请检查您的网络连接是否正常',
      retryable: true,
    };
  }

  // 超时错误
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return {
      type: ErrorType.TIMEOUT,
      message: '请求超时',
      details: '服务器响应时间过长，请稍后重试',
      retryable: true,
    };
  }

  // 服务器返回的错误
  if (error.response) {
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return {
          type: ErrorType.VALIDATION,
          message: '请求参数错误',
          details: data.detail || data.message || '请检查输入的内容',
          retryable: false,
        };

      case 413:
        return {
          type: ErrorType.UPLOAD,
          message: '文件太大',
          details: '文件大小超过限制（最大 200MB）',
          retryable: false,
        };

      case 415:
        return {
          type: ErrorType.UPLOAD,
          message: '不支持的文件类型',
          details: '请上传支持的文件格式（PDF、Word、图片等）',
          retryable: false,
        };

      case 500:
        return {
          type: ErrorType.AI_ANALYSIS,
          message: 'AI 分析失败',
          details: data.detail || '服务器处理出错，请稍后重试',
          retryable: true,
        };

      case 502:
      case 503:
      case 504:
        return {
          type: ErrorType.NETWORK,
          message: '服务暂时不可用',
          details: '服务器正忙或维护中，请稍后重试',
          retryable: true,
        };

      default:
        return {
          type: ErrorType.UNKNOWN,
          message: '操作失败',
          details: data.detail || data.message || `错误代码: ${status}`,
          retryable: true,
        };
    }
  }

  // 未知错误
  return {
    type: ErrorType.UNKNOWN,
    message: '发生未知错误',
    details: error.message || '请稍后重试',
    retryable: true,
  };
};

/**
 * 显示简单的错误提示
 */
export const showErrorMessage = (error: any, customMessage?: string) => {
  const errorInfo = parseApiError(error);
  message.error(customMessage || errorInfo.message);
};

/**
 * 显示详细的错误通知
 */
export const showErrorNotification = (
  error: any,
  options?: {
    title?: string;
    onRetry?: () => void | Promise<void>;
  }
) => {
  const errorInfo = parseApiError(error);

  const description = errorInfo.retryable && options?.onRetry
    ? `${errorInfo.details}\n\n点击右侧按钮重试`
    : errorInfo.details;

  notification.error({
    message: options?.title || errorInfo.message,
    description,
    duration: errorInfo.retryable ? 8 : 5,
    placement: 'topRight',
    btn: errorInfo.retryable && options?.onRetry ? (
      {
        key: 'retry',
        label: '重试',
        onClick: () => {
          notification.destroy();
          options.onRetry?.();
        },
      }
    ) : undefined,
  } as any);
};

/**
 * 显示错误确认对话框（带重试选项）
 */
export const showErrorModal = (
  error: any,
  options?: {
    title?: string;
    content?: string;
    onRetry?: () => void | Promise<void>;
    onCancel?: () => void;
  }
) => {
  const errorInfo = parseApiError(error);

  const content = errorInfo.retryable && options?.onRetry
    ? `${options?.content || errorInfo.details}\n\n您可以点击"重试"按钮再次尝试`
    : (options?.content || errorInfo.details);

  Modal.error({
    title: options?.title || errorInfo.message,
    content,
    okText: errorInfo.retryable && options?.onRetry ? '重试' : '确定',
    cancelText: errorInfo.retryable && options?.onRetry ? '取消' : undefined,
    onOk: errorInfo.retryable && options?.onRetry ? options.onRetry : undefined,
    onCancel: options?.onCancel,
  });
};

/**
 * 文件上传错误处理
 */
export const handleFileUploadError = (
  file: File,
  error: any,
  onRetry?: () => void
) => {
  const errorInfo = parseApiError(error);

  // 特殊处理文件大小错误
  if (file.size > 200 * 1024 * 1024) {
    showErrorNotification(
      { response: { status: 413 } },
      {
        title: `"${file.name}" 上传失败`,
      }
    );
    return;
  }

  // 特殊处理文件类型错误
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/markdown',
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/gif',
    'image/webp',
  ];

  if (!allowedTypes.includes(file.type)) {
    showErrorNotification(
      { response: { status: 415 } },
      {
        title: `"${file.name}" 上传失败`,
      }
    );
    return;
  }

  // 其他上传错误
  showErrorNotification(error, {
    title: `"${file.name}" 上传失败`,
    onRetry,
  });
};

/**
 * AI 分析错误处理
 */
export const handleAIAnalysisError = (
  fileName: string,
  error: any,
  onRetry?: () => void
) => {
  showErrorNotification(error, {
    title: `"${fileName}" AI 分析失败`,
    onRetry,
  });
};

/**
 * 网络超时错误处理
 */
export const handleTimeoutError = (
  operation: string,
  onRetry?: () => void
) => {
  const description = `${operation}耗时较长，可能由于：
• 文件较大，处理需要更多时间
• 网络连接不稳定
• 服务器负载较高

建议：减少文件数量或稍后重试`;

  notification.warning({
    message: '请求超时',
    description,
    duration: 10,
    placement: 'topRight',
    btn: onRetry ? (
      {
        key: 'retry',
        label: '重试',
        onClick: () => {
          notification.destroy();
          onRetry();
        },
      }
    ) : undefined,
  } as any);
};

/**
 * 批量操作错误处理
 */
export interface BatchError {
  item: string;
  error: any;
}

export const handleBatchErrors = (
  errors: BatchError[],
  successCount: number,
  totalCount: number
) => {
  if (errors.length === 0) {
    message.success(`全部 ${totalCount} 项操作成功！`);
    return;
  }

  if (successCount === 0) {
    notification.error({
      message: '批量操作失败',
      description: `全部 ${totalCount} 项操作失败，请检查后重试`,
      duration: 5,
    });
    return;
  }

  // 部分成功
  const failedItems = errors
    .map((err, idx) => `${idx + 1}. ${err.item} - ${parseApiError(err.error).message}`)
    .join('\n');

  Modal.warning({
    title: '批量操作部分失败',
    content: `成功：${successCount} 项，失败：${errors.length} 项\n\n失败项目：\n${failedItems}`,
    width: 500,
  });
};
