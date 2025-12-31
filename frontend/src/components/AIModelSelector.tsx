import { useState, useEffect } from 'react';
import { Select, message, Tooltip, Tag } from 'antd';
import { ThunderboltOutlined, RobotOutlined } from '@ant-design/icons';
import { aiModelsApi } from '../services/api';
import type { AIProvider, ProviderInfo } from '../types';

const { Option } = Select;

interface AIModelSelectorProps {
  size?: 'small' | 'middle' | 'large';
  style?: React.CSSProperties;
}

const AIModelSelector = ({ size = 'small', style }: AIModelSelectorProps) => {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [currentProvider, setCurrentProvider] = useState<AIProvider>('gemini');
  const [loading, setLoading] = useState(false);
  const [switching, setSwitching] = useState(false);

  // 加载可用的 AI 提供商
  const loadProviders = async () => {
    try {
      setLoading(true);
      const data = await aiModelsApi.getProviders();
      setProviders(data.providers);
      setCurrentProvider(data.current_provider as AIProvider);
    } catch (error) {
      console.error('Failed to load AI providers:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  // 切换 AI 模型
  const handleChange = async (value: AIProvider) => {
    try {
      setSwitching(true);
      const result = await aiModelsApi.selectProvider(value);
      setCurrentProvider(value);
      message.success({
        content: `已切换到 ${getProviderDisplayName(value)}`,
        duration: 2,
      });
    } catch (error: any) {
      console.error('Failed to switch provider:', error);
      const errorMsg = error.response?.data?.detail || '切换模型失败';
      message.error(errorMsg);
      // 恢复到之前的选择
      setCurrentProvider(currentProvider);
    } finally {
      setSwitching(false);
    }
  };

  // 获取提供商的显示名称
  const getProviderDisplayName = (provider: string): string => {
    switch (provider) {
      case 'gemini':
        return 'Google Gemini';
      case 'openai':
        return 'OpenAI GPT-4';
      case 'claude':
        return 'Anthropic Claude';
      default:
        return provider;
    }
  };

  // 获取提供商的标签颜色
  const getProviderColor = (provider: string): string => {
    switch (provider) {
      case 'gemini':
        return '#4285f4'; // Google blue
      case 'openai':
        return '#10a37f'; // OpenAI green
      case 'claude':
        return '#d97706'; // Claude orange
      default:
        return '#666';
    }
  };

  // 获取提供商的描述
  const getProviderDescription = (provider: ProviderInfo): string => {
    const base = `${provider.model}`;
    if (!provider.available) {
      return `${base} - 未配置`;
    }
    if (provider.name === 'gemini') {
      return `${base} - 免费`;
    }
    return base;
  };

  return (
    <Select
      value={currentProvider}
      onChange={handleChange}
      loading={loading || switching}
      disabled={loading || switching}
      size={size}
      style={{ minWidth: 180, ...style }}
      suffixIcon={<RobotOutlined />}
      popupMatchSelectWidth={false}
      styles={{ popup: { root: { minWidth: 250 } } }}
    >
      {providers.map((provider) => (
        <Option
          key={provider.name}
          value={provider.name}
          disabled={!provider.available}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>
              {getProviderDisplayName(provider.name)}
              {provider.current && (
                <Tag
                  color="blue"
                  style={{ marginLeft: 8, fontSize: '10px' }}
                >
                  当前
                </Tag>
              )}
            </span>
            <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
              {!provider.available && (
                <Tooltip title="需要在 .env 文件中配置 API 密钥">
                  <Tag color="red" style={{ margin: 0, fontSize: '10px' }}>
                    未配置
                  </Tag>
                </Tooltip>
              )}
              {provider.available && provider.name === 'gemini' && (
                <Tooltip title="免费使用">
                  <Tag color="green" style={{ margin: 0, fontSize: '10px' }}>
                    免费
                  </Tag>
                </Tooltip>
              )}
              {provider.available && provider.name !== 'gemini' && (
                <Tag color="orange" style={{ margin: 0, fontSize: '10px' }}>
                  付费
                </Tag>
              )}
            </div>
          </div>
          <div style={{ fontSize: '11px', color: '#999', marginTop: 2 }}>
            {getProviderDescription(provider)}
          </div>
        </Option>
      ))}
    </Select>
  );
};

export default AIModelSelector;
