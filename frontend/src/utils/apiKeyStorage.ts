/**
 * API Key Storage Utility
 * 管理用户的 AI API Keys，保存在浏览器 localStorage
 */

export interface APIKeys {
  gemini?: string;
  openai?: string;
  claude?: string;
  deepseek?: string;
  defaultProvider?: 'gemini' | 'openai' | 'claude' | 'deepseek';
}

const STORAGE_KEY = 'ai_api_keys';

/**
 * 获取所有保存的 API Keys
 */
export const getAPIKeys = (): APIKeys => {
  try {
    const keys = localStorage.getItem(STORAGE_KEY);
    return keys ? JSON.parse(keys) : {};
  } catch (error) {
    console.error('Failed to load API keys:', error);
    return {};
  }
};

/**
 * 保存 API Keys
 */
export const saveAPIKeys = (keys: APIKeys): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
  } catch (error) {
    console.error('Failed to save API keys:', error);
    throw new Error('保存 API Key 失败');
  }
};

/**
 * 获取单个 API Key
 */
export const getAPIKey = (provider: 'gemini' | 'openai' | 'claude' | 'deepseek'): string | undefined => {
  const keys = getAPIKeys();
  return keys[provider];
};

/**
 * 获取默认的 AI 提供商
 */
export const getDefaultProvider = (): 'gemini' | 'openai' | 'claude' | 'deepseek' => {
  const keys = getAPIKeys();
  return keys.defaultProvider || 'gemini';
};

/**
 * 检查是否配置了至少一个 API Key
 */
export const hasAnyAPIKey = (): boolean => {
  const keys = getAPIKeys();
  return !!(keys.gemini || keys.openai || keys.claude || keys.deepseek);
};

/**
 * 检查指定提供商是否配置了 API Key
 */
export const hasProviderKey = (provider: 'gemini' | 'openai' | 'claude' | 'deepseek'): boolean => {
  const keys = getAPIKeys();
  return !!keys[provider];
};

/**
 * 清除所有 API Keys
 */
export const clearAPIKeys = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear API keys:', error);
  }
};

/**
 * 脱敏显示 API Key（只显示前4位和后4位）
 */
export const maskAPIKey = (key: string): string => {
  if (!key || key.length < 8) return '••••••••';
  return `${key.substring(0, 4)}••••${key.substring(key.length - 4)}`;
};
