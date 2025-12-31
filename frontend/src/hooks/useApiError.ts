import { useCallback } from 'react';
import {
  showErrorMessage,
  showErrorNotification,
  showErrorModal,
  handleFileUploadError,
  handleAIAnalysisError,
  handleTimeoutError,
  parseApiError,
  ErrorType,
} from '../utils/errorHandler';

/**
 * API 错误处理 Hook
 */
export const useApiError = () => {
  /**
   * 简单错误提示
   */
  const showSimpleError = useCallback((error: any, customMessage?: string) => {
    showErrorMessage(error, customMessage);
  }, []);

  /**
   * 详细错误通知
   */
  const showDetailedError = useCallback(
    (
      error: any,
      options?: {
        title?: string;
        onRetry?: () => void | Promise<void>;
      }
    ) => {
      showErrorNotification(error, options);
    },
    []
  );

  /**
   * 错误对话框
   */
  const showErrorDialog = useCallback(
    (
      error: any,
      options?: {
        title?: string;
        content?: string;
        onRetry?: () => void | Promise<void>;
        onCancel?: () => void;
      }
    ) => {
      showErrorModal(error, options);
    },
    []
  );

  /**
   * 文件上传错误
   */
  const handleUploadError = useCallback(
    (file: File, error: any, onRetry?: () => void) => {
      handleFileUploadError(file, error, onRetry);
    },
    []
  );

  /**
   * AI 分析错误
   */
  const handleAnalysisError = useCallback(
    (fileName: string, error: any, onRetry?: () => void) => {
      handleAIAnalysisError(fileName, error, onRetry);
    },
    []
  );

  /**
   * 超时错误
   */
  const handleTimeout = useCallback((operation: string, onRetry?: () => void) => {
    handleTimeoutError(operation, onRetry);
  }, []);

  /**
   * 获取错误信息
   */
  const getErrorInfo = useCallback((error: any) => {
    return parseApiError(error);
  }, []);

  /**
   * 判断是否可重试
   */
  const isRetryable = useCallback((error: any) => {
    const errorInfo = parseApiError(error);
    return errorInfo.retryable || false;
  }, []);

  /**
   * 判断是否为网络错误
   */
  const isNetworkError = useCallback((error: any) => {
    const errorInfo = parseApiError(error);
    return errorInfo.type === ErrorType.NETWORK;
  }, []);

  /**
   * 判断是否为超时错误
   */
  const isTimeoutError = useCallback((error: any) => {
    const errorInfo = parseApiError(error);
    return errorInfo.type === ErrorType.TIMEOUT;
  }, []);

  return {
    showSimpleError,
    showDetailedError,
    showErrorDialog,
    handleUploadError,
    handleAnalysisError,
    handleTimeout,
    getErrorInfo,
    isRetryable,
    isNetworkError,
    isTimeoutError,
  };
};
