import { useState, useEffect } from 'react';
import { Card, Input, Button, Space, Typography, Select, message, Divider, Alert, Tabs } from 'antd';
import { EyeOutlined, EyeInvisibleOutlined, SaveOutlined, DeleteOutlined, CheckCircleOutlined, ThunderboltOutlined, LoadingOutlined } from '@ant-design/icons';
import { getAPIKeys, saveAPIKeys, clearAPIKeys, maskAPIKey, type APIKeys } from '../utils/apiKeyStorage';
import { aiModelsApi } from '../services/api';

const { Title, Text, Paragraph } = Typography;

interface ProviderConfig {
  name: string;
  key: keyof APIKeys;
  placeholder: string;
  description: string;
  getKeyUrl: string;
  color: string;
}

const PROVIDERS: ProviderConfig[] = [
  {
    name: 'Google Gemini 2.0',
    key: 'gemini',
    placeholder: 'AIza...',
    description: '最新多模态模型，免费使用',
    getKeyUrl: 'https://makersuite.google.com/app/apikey',
    color: '#4285f4',
  },
  {
    name: 'OpenAI GPT-5.2',
    key: 'openai',
    placeholder: 'sk-...',
    description: '最强推理能力，支持思考模式',
    getKeyUrl: 'https://platform.openai.com/api-keys',
    color: '#10a37f',
  },
  {
    name: 'Claude Opus 4.5',
    key: 'claude',
    placeholder: 'sk-ant-...',
    description: '最新旗舰模型，擅长复杂任务',
    getKeyUrl: 'https://console.anthropic.com/settings/keys',
    color: '#d97706',
  },
  {
    name: 'DeepSeek V3.2',
    key: 'deepseek',
    placeholder: 'sk-...',
    description: '强化 Agent 能力，融入思考推理',
    getKeyUrl: 'https://platform.deepseek.com/api-keys',
    color: '#7c3aed',
  },
];

const APIKeySettings = () => {
  const [keys, setKeys] = useState<APIKeys>({});
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState<Record<string, boolean>>({});
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({});

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = () => {
    const savedKeys = getAPIKeys();
    setKeys(savedKeys);
  };

  const handleKeyChange = (provider: keyof APIKeys, value: string) => {
    setKeys({ ...keys, [provider]: value });
  };

  const toggleKeyVisibility = (provider: string) => {
    setVisibleKeys({ ...visibleKeys, [provider]: !visibleKeys[provider] });
  };

  const handleSave = () => {
    try {
      setSaving(true);

      // 验证至少配置了一个 Key
      const hasKey = Object.entries(keys).some(
        ([key, value]) => key !== 'defaultProvider' && value && value.trim()
      );

      if (!hasKey) {
        message.warning('请至少配置一个 AI 模型的 API Key');
        return;
      }

      // 如果没有设置默认提供商，自动选择第一个配置的
      if (!keys.defaultProvider) {
        for (const provider of PROVIDERS) {
          if (keys[provider.key]) {
            keys.defaultProvider = provider.key as any;
            break;
          }
        }
      }

      saveAPIKeys(keys);
      message.success('API Key 配置已保存');
    } catch (error: any) {
      message.error(error.message || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleClear = () => {
    clearAPIKeys();
    setKeys({});
    setTestResults({});
    message.success('已清除所有 API Key');
  };

  const handleTest = async (provider: keyof APIKeys) => {
    const apiKey = keys[provider] as string;
    if (!apiKey || !apiKey.trim()) {
      message.warning('请先输入 API Key');
      return;
    }

    setTesting({ ...testing, [provider]: true });
    setTestResults({ ...testResults, [provider]: { success: false, message: '测试中...' } });

    try {
      const result = await aiModelsApi.testAPIKey(provider as any, apiKey);

      setTestResults({
        ...testResults,
        [provider]: {
          success: result.success,
          message: result.success
            ? `✅ ${result.message} (${result.model_name})`
            : `❌ ${result.message}${result.error ? `: ${result.error}` : ''}`,
        },
      });

      if (result.success) {
        message.success(`${PROVIDERS.find(p => p.key === provider)?.name} API Key 验证成功！`);
      } else {
        message.error(`${PROVIDERS.find(p => p.key === provider)?.name} API Key 验证失败`);
      }
    } catch (error: any) {
      console.error('API Key test failed:', error);
      setTestResults({
        ...testResults,
        [provider]: {
          success: false,
          message: `❌ 测试失败: ${error.message || '网络错误'}`,
        },
      });
      message.error('测试失败，请检查网络连接');
    } finally {
      setTesting({ ...testing, [provider]: false });
    }
  };

  const renderProviderCard = (provider: ProviderConfig) => {
    const currentValue = keys[provider.key] as string || '';
    const isConfigured = !!currentValue;
    const testResult = testResults[provider.key];
    const isTesting = testing[provider.key];

    return (
      <Card
        key={provider.key}
        size="small"
        style={{ marginBottom: 16 }}
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: provider.color,
                }}
              />
              <Text strong>{provider.name}</Text>
            </div>
            {isConfigured && <CheckCircleOutlined style={{ color: '#52c41a' }} />}
          </div>
        }
      >
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {provider.description}
          </Text>

          <Input.Password
            placeholder={provider.placeholder}
            value={currentValue}
            onChange={(e) => {
              handleKeyChange(provider.key, e.target.value);
              // 清除之前的测试结果
              if (testResults[provider.key]) {
                setTestResults({ ...testResults, [provider.key]: undefined as any });
              }
            }}
            iconRender={(visible) =>
              visible ? <EyeOutlined /> : <EyeInvisibleOutlined />
            }
            visibilityToggle={{
              visible: visibleKeys[provider.key],
              onVisibleChange: () => toggleKeyVisibility(provider.key),
            }}
            style={{ fontFamily: 'monospace' }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
            <a
              href={provider.getKeyUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ fontSize: 12 }}
            >
              获取 API Key →
            </a>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {currentValue && (
                <>
                  <Button
                    size="small"
                    icon={isTesting ? <LoadingOutlined /> : <ThunderboltOutlined />}
                    onClick={() => handleTest(provider.key)}
                    loading={isTesting}
                    type="link"
                  >
                    测试
                  </Button>
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {maskAPIKey(currentValue)}
                  </Text>
                </>
              )}
            </div>
          </div>

          {/* 测试结果显示 */}
          {testResult && (
            <Alert
              message={testResult.message}
              type={testResult.success ? 'success' : 'error'}
              showIcon
              closable
              onClose={() => {
                const newResults = { ...testResults };
                delete newResults[provider.key];
                setTestResults(newResults);
              }}
              style={{ fontSize: 12 }}
            />
          )}
        </Space>
      </Card>
    );
  };

  const configuredCount = PROVIDERS.filter((p) => keys[p.key]).length;

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 头部 */}
        <div>
          <Title level={3}>AI API Key 配置</Title>
          <Paragraph type="secondary">
            配置您的 AI 模型 API Key，PRD Sherpa 将使用您自己的额度进行需求分析。
            <br />
            API Key 仅保存在浏览器本地，不会上传到服务器。
          </Paragraph>
        </div>

        {/* 状态提示 */}
        {configuredCount === 0 ? (
          <Alert
            message="尚未配置 API Key"
            description="请至少配置一个 AI 模型的 API Key 才能使用 PRD Sherpa 的 AI 功能。"
            type="warning"
            showIcon
          />
        ) : (
          <Alert
            message={`已配置 ${configuredCount} 个 AI 模型`}
            description="您可以在下方管理或添加更多 API Key。"
            type="success"
            showIcon
          />
        )}

        {/* 默认模型选择 */}
        {configuredCount > 0 && (
          <Card size="small">
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text strong>默认 AI 模型</Text>
              <Select
                value={keys.defaultProvider}
                onChange={(value) => setKeys({ ...keys, defaultProvider: value })}
                style={{ width: '100%' }}
                options={PROVIDERS.filter((p) => keys[p.key]).map((p) => ({
                  label: p.name,
                  value: p.key,
                }))}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>
                新建对话时默认使用的 AI 模型
              </Text>
            </Space>
          </Card>
        )}

        <Divider orientation="left">API Key 配置</Divider>

        {/* API Key 输入区域 */}
        <div>
          {PROVIDERS.map((provider) => renderProviderCard(provider))}
        </div>

        {/* 操作按钮 */}
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={handleClear}
            disabled={configuredCount === 0}
          >
            清除所有配置
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            保存配置
          </Button>
        </div>

        {/* 使用说明 */}
        <Card size="small" style={{ background: '#fafafa' }}>
          <Title level={5}>使用说明</Title>
          <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, lineHeight: 1.8 }}>
            <li>API Key 保存在浏览器 localStorage，不会上传到服务器</li>
            <li>每次 AI 请求会使用对应模型的 API Key</li>
            <li>更换浏览器或清除缓存后需要重新配置</li>
            <li>建议配置至少一个模型，推荐 Gemini（免费）</li>
            <li>可以配置多个模型并随时切换使用</li>
          </ul>
        </Card>
      </Space>
    </div>
  );
};

export default APIKeySettings;
