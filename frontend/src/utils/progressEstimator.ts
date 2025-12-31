/**
 * 进度估算工具
 * 用于估算文件上传、分析、知识库构建等操作的时间
 */

/**
 * 文件大小估算（MB -> 秒）
 * 基于网络速度和处理速度
 */
export const estimateFileUploadTime = (fileSizeMB: number): number => {
  // 假设上传速度: 5MB/s (较慢的网络)
  const uploadSpeed = 5;
  return Math.ceil(fileSizeMB / uploadSpeed);
};

/**
 * 文件分析时间估算
 * 不同文件类型处理时间不同
 */
export const estimateFileAnalysisTime = (fileType: string, fileSizeMB: number): number => {
  const baseTime: Record<string, number> = {
    'image': 5,        // 图片分析基础时间: 5秒
    'pdf': 10,         // PDF分析基础时间: 10秒
    'doc': 8,          // Word文档: 8秒
    'docx': 8,
    'ppt': 12,         // PPT: 12秒
    'pptx': 12,
    'txt': 3,          // 文本文件: 3秒
    'md': 3,
    'default': 8,      // 默认: 8秒
  };

  // 获取文件类型的基础时间
  const fileTypeKey = Object.keys(baseTime).find(key => fileType.includes(key)) || 'default';
  const base = baseTime[fileTypeKey];

  // 根据文件大小调整时间（每10MB增加1秒）
  const sizeAdjustment = Math.ceil(fileSizeMB / 10);

  return base + sizeAdjustment;
};

/**
 * 知识库构建时间估算
 * 基于文件数量
 */
export const estimateKnowledgeBuildTime = (fileCount: number): number => {
  // 基础时间: 15秒
  // 每个文件增加: 5秒
  const baseTime = 15;
  const perFileTime = 5;

  return baseTime + (fileCount * perFileTime);
};

/**
 * 批量操作进度计算器
 */
export class ProgressCalculator {
  private total: number;
  private completed: number;
  private startTime: number;
  private estimatedTotalTime: number;

  constructor(total: number, estimatedTotalTime?: number) {
    this.total = total;
    this.completed = 0;
    this.startTime = Date.now();
    this.estimatedTotalTime = estimatedTotalTime || 0;
  }

  /**
   * 更新进度
   */
  update(completed: number) {
    this.completed = completed;
  }

  /**
   * 增加完成数
   */
  increment() {
    this.completed++;
  }

  /**
   * 获取进度百分比
   */
  getProgress(): number {
    return this.total > 0 ? Math.round((this.completed / this.total) * 100) : 0;
  }

  /**
   * 获取已用时间（秒）
   */
  getElapsedTime(): number {
    return Math.floor((Date.now() - this.startTime) / 1000);
  }

  /**
   * 获取预估剩余时间（秒）
   * 基于实际进度动态调整
   */
  getEstimatedRemainingTime(): number {
    if (this.completed === 0) {
      return this.estimatedTotalTime;
    }

    const elapsed = this.getElapsedTime();
    const avgTimePerItem = elapsed / this.completed;
    const remaining = this.total - this.completed;

    return Math.ceil(avgTimePerItem * remaining);
  }

  /**
   * 获取预估总时间（秒）
   */
  getEstimatedTotalTime(): number {
    if (this.completed === 0) {
      return this.estimatedTotalTime;
    }

    const elapsed = this.getElapsedTime();
    const avgTimePerItem = elapsed / this.completed;

    return Math.ceil(avgTimePerItem * this.total);
  }

  /**
   * 是否完成
   */
  isCompleted(): boolean {
    return this.completed >= this.total;
  }

  /**
   * 重置
   */
  reset(total?: number) {
    if (total !== undefined) {
      this.total = total;
    }
    this.completed = 0;
    this.startTime = Date.now();
  }
}

/**
 * 格式化时间显示
 */
export const formatTime = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds} 秒`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes} 分 ${remainingSeconds} 秒`
      : `${minutes} 分钟`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  return `${hours} 小时 ${remainingMinutes} 分钟`;
};

/**
 * 知识库构建阶段进度计算
 */
export class KnowledgeBuildProgress {
  private stages = [
    { key: 'analyzing_files', progress: 25, duration: 0.3 },
    { key: 'extracting_info', progress: 50, duration: 0.4 },
    { key: 'building_structure', progress: 75, duration: 0.2 },
    { key: 'completing', progress: 95, duration: 0.1 },
  ];

  private currentStageIndex: number = 0;
  private startTime: number;
  private totalDuration: number;

  constructor(estimatedDuration: number) {
    this.startTime = Date.now();
    this.totalDuration = estimatedDuration;
  }

  /**
   * 获取当前阶段
   */
  getCurrentStage(): string {
    const elapsed = (Date.now() - this.startTime) / 1000;
    const progress = Math.min(elapsed / this.totalDuration, 1);

    for (let i = 0; i < this.stages.length; i++) {
      if (progress <= this.stages[i].progress / 100) {
        this.currentStageIndex = i;
        return this.stages[i].key;
      }
    }

    return this.stages[this.stages.length - 1].key;
  }

  /**
   * 获取当前进度百分比
   */
  getProgress(): number {
    const elapsed = (Date.now() - this.startTime) / 1000;
    return Math.min(Math.round((elapsed / this.totalDuration) * 100), 99);
  }

  /**
   * 获取剩余时间（秒）
   */
  getRemainingTime(): number {
    const elapsed = (Date.now() - this.startTime) / 1000;
    return Math.max(Math.ceil(this.totalDuration - elapsed), 0);
  }

  /**
   * 手动设置阶段
   */
  setStage(stageKey: string) {
    const index = this.stages.findIndex(s => s.key === stageKey);
    if (index !== -1) {
      this.currentStageIndex = index;
    }
  }
}
