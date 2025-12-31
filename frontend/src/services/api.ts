import axios from 'axios';
import type {
  Project,
  ProjectCreate,
  UploadedFile,
  KnowledgeBase,
  Conversation,
  ConversationDetail,
  ChatRequest,
  ChatResponse,
  ExportResponse,
  ConversationStatusUpdate,
  PRDDraft,
  SearchResponse,
  AIProvider,
  ProvidersListResponse,
  CurrentProviderResponse,
} from '../types';
import { getAPIKeys, getDefaultProvider } from '../utils/apiKeyStorage';

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 180000, // 180 秒超时（3分钟），用于图片分析等耗时操作
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加用户配置的 AI API Keys
    const apiKeys = getAPIKeys();
    const defaultProvider = getDefaultProvider();

    // 如果用户配置了默认提供商和对应的 API Key，则添加到请求头
    if (defaultProvider && apiKeys[defaultProvider]) {
      config.headers['X-AI-Provider'] = defaultProvider;
      config.headers['X-AI-API-Key'] = apiKeys[defaultProvider];
    }

    // 可以在这里添加认证 token
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 增强的错误处理
    if (error.response) {
      // 服务器返回错误
      console.error('API Error:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url,
      });
    } else if (error.request) {
      // 请求发送但没有响应（网络错误）
      console.error('Network Error:', {
        message: error.message,
        url: error.config?.url,
      });
    } else {
      // 其他错误
      console.error('Error:', error.message);
    }

    // 添加错误上下文信息
    error.context = {
      url: error.config?.url,
      method: error.config?.method,
      timestamp: new Date().toISOString(),
    };

    return Promise.reject(error);
  }
);

// ============ 项目管理 API ============

export const projectApi = {
  // 创建项目
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await api.post<Project>('/api/projects/', data);
    return response.data;
  },

  // 获取项目列表
  list: async (): Promise<Project[]> => {
    const response = await api.get<{ projects: Project[]; total: number }>('/api/projects/');
    return response.data.projects;
  },

  // 获取项目详情
  get: async (id: string): Promise<Project> => {
    const response = await api.get<Project>(`/api/projects/${id}`);
    return response.data;
  },

  // 更新项目
  update: async (id: string, data: Partial<ProjectCreate>): Promise<Project> => {
    const response = await api.patch<Project>(`/api/projects/${id}`, data);
    return response.data;
  },

  // 删除项目
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/projects/${id}`);
  },
};

// ============ 文件管理 API ============

export const fileApi = {
  // 上传文件
  upload: async (projectId: string, file: File): Promise<UploadedFile> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    const response = await api.post<UploadedFile>('/api/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 分析文件
  analyze: async (fileId: string): Promise<UploadedFile> => {
    const response = await api.post<UploadedFile>(`/api/files/${fileId}/analyze`);
    return response.data;
  },

  // 获取项目文件列表
  listByProject: async (projectId: string): Promise<UploadedFile[]> => {
    const response = await api.get<UploadedFile[]>(`/api/files/project/${projectId}`);
    return response.data;
  },

  // 删除文件
  delete: async (fileId: string): Promise<void> => {
    await api.delete(`/api/files/${fileId}`);
  },
};

// ============ 知识库 API ============

export const knowledgeApi = {
  // 构建知识库
  build: async (projectId: string, fileIds: string[]): Promise<KnowledgeBase> => {
    const response = await api.post<KnowledgeBase>(
      `/api/knowledge/build/${projectId}`,
      { file_ids: fileIds }
    );
    return response.data;
  },

  // 获取知识库
  get: async (projectId: string): Promise<KnowledgeBase> => {
    const response = await api.get<KnowledgeBase>(`/api/knowledge/${projectId}`);
    return response.data;
  },

  // 更新知识库
  update: async (projectId: string, data: Partial<KnowledgeBase>): Promise<KnowledgeBase> => {
    const response = await api.patch<KnowledgeBase>(`/api/knowledge/${projectId}`, data);
    return response.data;
  },

  // 确认知识库
  confirm: async (projectId: string, confirmedBy: string): Promise<KnowledgeBase> => {
    const response = await api.post<KnowledgeBase>(
      `/api/knowledge/${projectId}/confirm`,
      { confirmed_by: confirmedBy }
    );
    return response.data;
  },
};

// ============ 对话 API ============

export const conversationApi = {
  // 创建对话
  create: async (projectId: string, title?: string): Promise<Conversation> => {
    const response = await api.post<Conversation>('/api/conversations/', {
      project_id: projectId,
      title,
    });
    return response.data;
  },

  // 获取项目对话列表
  listByProject: async (projectId: string): Promise<Conversation[]> => {
    const response = await api.get<{ conversations: Conversation[] }>(
      `/api/conversations/project/${projectId}`
    );
    return response.data.conversations;
  },

  // 获取对话详情
  get: async (conversationId: string): Promise<ConversationDetail> => {
    const response = await api.get<ConversationDetail>(`/api/conversations/${conversationId}`);
    return response.data;
  },

  // 发送消息
  chat: async (conversationId: string, message: string, imageFileIds?: string[]): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>(
      `/api/conversations/${conversationId}/chat`,
      {
        message,
        image_file_ids: imageFileIds
      }
    );
    return response.data;
  },

  // 更新对话状态
  updateStatus: async (
    conversationId: string,
    status: 'active' | 'completed' | 'archived',
    generateSummary = true
  ): Promise<Conversation> => {
    const response = await api.patch<Conversation>(
      `/api/conversations/${conversationId}/status`,
      {
        status,
        generate_summary: generateSummary,
      }
    );
    return response.data;
  },

  // 更新对话标题
  updateTitle: async (conversationId: string, title: string): Promise<Conversation> => {
    const response = await api.patch<Conversation>(
      `/api/conversations/${conversationId}/title`,
      { title }
    );
    return response.data;
  },

  // 删除对话
  delete: async (conversationId: string): Promise<void> => {
    await api.delete(`/api/conversations/${conversationId}`);
  },
};

// ============ 导出 API ============

export const exportApi = {
  // 导出 PRD (JSON)
  export: async (conversationId: string, includeKb = true): Promise<ExportResponse> => {
    const response = await api.post<ExportResponse>(
      `/api/export/conversation/${conversationId}`,
      null,
      { params: { include_knowledge_base: includeKb } }
    );
    return response.data;
  },

  // 下载 PRD 文件（支持多种格式）
  download: async (
    conversationId: string,
    format: 'markdown' | 'word' | 'html' | 'pdf' = 'markdown',
    includeKb = true
  ): Promise<Blob> => {
    const response = await api.get(`/api/export/conversation/${conversationId}/download`, {
      params: {
        format,
        include_knowledge_base: includeKb,
      },
      responseType: 'blob',
    });
    return response.data;
  },
};

// ============ PRD API ============

export const prdApi = {
  // Generate PRD outline
  generateOutline: async (conversationId: string): Promise<PRDDraft> => {
    const response = await api.post<PRDDraft>(
      `/api/prd/${conversationId}/outline`
    );
    return response.data;
  },

  // Get PRD draft
  getDraft: async (conversationId: string): Promise<PRDDraft> => {
    const response = await api.get<PRDDraft>(
      `/api/prd/${conversationId}/draft`
    );
    return response.data;
  },

  // Update PRD section
  updateSection: async (
    conversationId: string,
    sectionKey: string,
    content: string
  ): Promise<PRDDraft> => {
    const response = await api.patch<PRDDraft>(
      `/api/prd/${conversationId}/section`,
      { section_key: sectionKey, content }
    );
    return response.data;
  },

  // Regenerate PRD section
  regenerateSection: async (
    conversationId: string,
    sectionKey: string
  ): Promise<PRDDraft> => {
    const response = await api.post<PRDDraft>(
      `/api/prd/${conversationId}/section/${sectionKey}/regenerate`
    );
    return response.data;
  },
};

// ============ Search API ============

export const searchApi = {
  // Search knowledge base
  searchKnowledge: async (
    projectId: string,
    query: string,
    filters?: {
      module?: string;
      type?: 'requirement' | 'module' | 'tech' | 'ui';
    }
  ): Promise<SearchResponse> => {
    const params: any = { q: query };
    if (filters?.module) params.module = filters.module;
    if (filters?.type) params.type = filters.type;

    const response = await api.get<SearchResponse>(
      `/api/search/knowledge/${projectId}`,
      { params }
    );
    return response.data;
  },
};

// ============ AI Models API ============

export const aiModelsApi = {
  // 获取所有可用的 AI 提供商
  getProviders: async (): Promise<ProvidersListResponse> => {
    const response = await api.get<ProvidersListResponse>('/api/ai/providers');
    return response.data;
  },

  // 切换 AI 提供商
  selectProvider: async (provider: AIProvider): Promise<any> => {
    const response = await api.post('/api/ai/provider/select', { provider });
    return response.data;
  },

  // 获取当前 AI 提供商
  getCurrentProvider: async (): Promise<CurrentProviderResponse> => {
    const response = await api.get<CurrentProviderResponse>('/api/ai/provider/current');
    return response.data;
  },

  // 测试 API Key 是否有效
  testAPIKey: async (
    provider: AIProvider,
    apiKey: string
  ): Promise<{
    success: boolean;
    message: string;
    model_name?: string;
    error?: string;
  }> => {
    const response = await api.post('/api/ai/test', {
      provider,
      api_key: apiKey,
    });
    return response.data;
  },
};

// ============ Wireframe API ============

export const wireframeApi = {
  // 生成线框图
  generate: async (
    conversationId: string,
    deviceType: 'mobile' | 'tablet' | 'desktop' = 'mobile',
    referenceFileIds: string[] = []
  ): Promise<{
    html_content: string;
    device_type: string;
    created_at: string;
  }> => {
    const response = await api.post(
      `/api/conversations/${conversationId}/wireframe`,
      {
        device_type: deviceType,
        reference_file_ids: referenceFileIds
      },
      {
        timeout: 60000, // 60秒超时，AI 生成线框图可能需要较长时间
      }
    );
    return response.data;
  },
};

export default api;

