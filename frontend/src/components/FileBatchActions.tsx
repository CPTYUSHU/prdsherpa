import { useState } from 'react';
import { Button, Space, message, Popconfirm, Checkbox, Modal } from 'antd';
import {
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
  CheckSquareOutlined,
  BorderOutlined,
} from '@ant-design/icons';
import type { UploadedFile } from '../types';
import { fileApi } from '../services/api';
import { useApiError } from '../hooks/useApiError';
import { handleBatchErrors, type BatchError } from '../utils/errorHandler';

interface FileBatchActionsProps {
  files: UploadedFile[];
  selectedFileIds: string[];
  onSelectionChange: (fileIds: string[]) => void;
  onFilesDeleted?: () => void;
  onFilesReanalyzed?: () => void;
}

/**
 * 批量文件操作组件
 */
const FileBatchActions = ({
  files,
  selectedFileIds,
  onSelectionChange,
  onFilesDeleted,
  onFilesReanalyzed,
}: FileBatchActionsProps) => {
  const { showDetailedError } = useApiError();
  const [deleting, setDeleting] = useState(false);
  const [reanalyzing, setReanalyzing] = useState(false);

  // 全选/取消全选
  const handleSelectAll = () => {
    if (selectedFileIds.length === files.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(files.map(f => f.id));
    }
  };

  // 批量删除文件
  const handleBatchDelete = async () => {
    if (selectedFileIds.length === 0) {
      message.warning('请先选择要删除的文件');
      return;
    }

    try {
      setDeleting(true);
      const errors: BatchError[] = [];
      let successCount = 0;

      for (const fileId of selectedFileIds) {
        try {
          await fileApi.delete(fileId);
          successCount++;
        } catch (error: any) {
          const file = files.find(f => f.id === fileId);
          errors.push({
            item: file?.filename || fileId,
            error,
          });
        }
      }

      // 处理批量结果
      handleBatchErrors(errors, successCount, selectedFileIds.length);

      // 清空选择
      onSelectionChange([]);

      // 回调
      if (onFilesDeleted) {
        onFilesDeleted();
      }
    } catch (error: any) {
      showDetailedError(error, {
        title: '批量删除失败',
      });
    } finally {
      setDeleting(false);
    }
  };

  // 批量重新分析
  const handleBatchReanalyze = async () => {
    if (selectedFileIds.length === 0) {
      message.warning('请先选择要重新分析的文件');
      return;
    }

    try {
      setReanalyzing(true);
      const errors: BatchError[] = [];
      let successCount = 0;

      for (const fileId of selectedFileIds) {
        try {
          await fileApi.analyze(fileId);
          successCount++;
        } catch (error: any) {
          const file = files.find(f => f.id === fileId);
          errors.push({
            item: file?.filename || fileId,
            error,
          });
        }
      }

      // 处理批量结果
      handleBatchErrors(errors, successCount, selectedFileIds.length);

      // 回调
      if (onFilesReanalyzed) {
        onFilesReanalyzed();
      }
    } catch (error: any) {
      showDetailedError(error, {
        title: '批量重新分析失败',
      });
    } finally {
      setReanalyzing(false);
    }
  };

  if (files.length === 0) {
    return null;
  }

  const allSelected = selectedFileIds.length === files.length && files.length > 0;
  const someSelected = selectedFileIds.length > 0 && selectedFileIds.length < files.length;

  return (
    <div style={{ marginBottom: '16px', padding: '12px', background: '#f5f5f5', borderRadius: '8px' }}>
      <Space wrap>
        {/* 全选按钮 */}
        <Button
          icon={allSelected ? <CheckSquareOutlined /> : <BorderOutlined />}
          onClick={handleSelectAll}
        >
          {allSelected ? '取消全选' : '全选'} ({selectedFileIds.length}/{files.length})
        </Button>

        {/* 批量删除 */}
        {selectedFileIds.length > 0 && (
          <Popconfirm
            title="批量删除文件"
            description={`确定要删除选中的 ${selectedFileIds.length} 个文件吗？`}
            onConfirm={handleBatchDelete}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              danger
              icon={<DeleteOutlined />}
              loading={deleting}
              disabled={deleting}
            >
              批量删除
            </Button>
          </Popconfirm>
        )}

        {/* 批量重新分析 */}
        {selectedFileIds.length > 0 && (
          <Popconfirm
            title="批量重新分析"
            description={`确定要重新分析选中的 ${selectedFileIds.length} 个文件吗？`}
            onConfirm={handleBatchReanalyze}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<ReloadOutlined />}
              loading={reanalyzing}
              disabled={reanalyzing}
            >
              批量重新分析
            </Button>
          </Popconfirm>
        )}
      </Space>
    </div>
  );
};

export default FileBatchActions;
