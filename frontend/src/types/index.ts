// API 响应类型定义

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  last_conversation_at?: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface UploadedFile {
  id: string;
  project_id: string;
  filename: string;
  file_path: string;
  file_type: string;
  file_size: number;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  analysis_result?: any;
  created_at: string;
}

export interface SystemOverview {
  product_type?: string;
  core_modules?: string[];
  description?: string;
}

export interface UIStandards {
  primary_colors?: string[];
  component_library?: string;
  layout_features?: string[];
  screenshots?: string[];
}

export interface TechConventions {
  naming_style?: string;
  api_style?: string;
  known_fields?: Array<{ name: string; type: string; description?: string }>;
}

export interface PendingQuestion {
  question: string;
  category: string;
}

export interface CompletedRequirement {
  conversation_id: string;
  title: string;
  description: string;
  key_points: string[];
  prd_generated: boolean;
  archived_at: string;
}

export interface FeatureModule {
  module_name: string;
  description: string;
  features: Array<{
    name: string;
    description: string;
    status: string;
    conversation_id: string;
    key_points: string[];
    completed_at: string;
  }>;
}

export interface ProjectOverview {
  description: string;
  product_type?: string;
  current_status: {
    total_requirements: number;
    completed_features: string[];
    feature_count_by_module: Record<string, number>;
  };
}

export interface TechArchitecture {
  conventions?: Record<string, any>;
  patterns: string[];
}

export interface KnowledgeBaseData {
  // Legacy fields (from initial KB setup)
  system_overview?: SystemOverview;
  ui_standards?: UIStandards;
  tech_conventions?: TechConventions;
  pending_questions?: PendingQuestion[];
  completed_requirements?: CompletedRequirement[];

  // New evolved fields (from knowledge evolution)
  project_overview?: ProjectOverview;
  feature_modules?: FeatureModule[];
  tech_architecture?: TechArchitecture;
  ui_ux_standards?: UIStandards;
}

export interface KnowledgeBase {
  id: string;
  project_id: string;
  structured_data: KnowledgeBaseData;
  version: number;
  status: 'draft' | 'confirmed';
  confirmed_by?: string;
  confirmed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  sequence: number;
  created_at: string;
}

export interface RequirementSummary {
  title: string;
  description: string;
  key_points: string[];
  prd_generated: boolean;
}

export interface Conversation {
  id: string;
  project_id: string;
  title: string;
  status: 'active' | 'completed' | 'archived';
  requirement_summary?: RequirementSummary;
  message_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface ConversationStatusUpdate {
  status: 'active' | 'completed' | 'archived';
  generate_summary?: boolean;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
  conversation_id: string;
}

export interface ExportResponse {
  content: string;
  format: string;
  filename: string;
}

// PRD Draft types
export interface PRDSection {
  title: string;
  content: string;
  status: 'empty' | 'outline' | 'draft' | 'completed';
  updated_at: string;
}

export interface PRDDraft {
  version: number;
  last_updated: string;
  sections: Record<string, PRDSection>;
}

export interface PRDSectionUpdate {
  section_key: string;
  content: string;
}

// Search types
export interface SearchResult {
  type: 'requirement' | 'module' | 'tech_pattern' | 'ui_component' | 'ui_pattern';
  title: string;
  description: string;
  content: string;
  conversation_id?: string;
  module_name?: string;
  tags: string[];
  created_at?: string;
  relevance_score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
}

// AI 模型管理类型
export type AIProvider = 'gemini' | 'openai' | 'claude';

export interface ProviderInfo {
  name: string;
  available: boolean;
  model: string;
  supports_streaming: boolean;
  supports_images: boolean;
  current: boolean;
}

export interface ProvidersListResponse {
  providers: ProviderInfo[];
  current_provider: string;
}

export interface CurrentProviderResponse {
  provider: AIProvider;
  model_name: string;
  provider_name: string;
}

