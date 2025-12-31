import { useState, useEffect } from 'react';
import {
  Input,
  Select,
  Card,
  Space,
  Typography,
  Empty,
  Tag,
  List,
  Badge,
  Spin,
  message,
  Button,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  FolderOutlined,
  ToolOutlined,
  BgColorsOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { searchApi } from '../services/api';
import type { SearchResult } from '../types';

const { Text, Paragraph } = Typography;
const { Search } = Input;

interface KnowledgeSearchProps {
  projectId: string;
  availableModules?: string[];
}

const KnowledgeSearch = ({ projectId, availableModules = [] }: KnowledgeSearchProps) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [typeFilter, setTypeFilter] = useState<string | undefined>(undefined);
  const [moduleFilter, setModuleFilter] = useState<string | undefined>(undefined);

  // 执行搜索
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }

    try {
      setSearching(true);
      const response = await searchApi.searchKnowledge(projectId, query, {
        type: typeFilter as any,
        module: moduleFilter,
      });
      setResults(response.results);
      setTotal(response.total);
    } catch (error: any) {
      console.error('Search failed:', error);
      message.error('搜索失败');
    } finally {
      setSearching(false);
    }
  };

  // 当筛选条件变化时重新搜索
  useEffect(() => {
    if (searchQuery) {
      handleSearch(searchQuery);
    }
  }, [typeFilter, moduleFilter]);

  // 获取类型图标和颜色
  const getTypeConfig = (type: string) => {
    const configs: Record<string, { icon: any; color: string; label: string }> = {
      requirement: { icon: <CheckCircleOutlined />, color: 'green', label: '需求' },
      module: { icon: <FolderOutlined />, color: 'blue', label: '模块' },
      tech_pattern: { icon: <ToolOutlined />, color: 'purple', label: '技术模式' },
      ui_component: { icon: <BgColorsOutlined />, color: 'orange', label: 'UI组件' },
      ui_pattern: { icon: <BgColorsOutlined />, color: 'cyan', label: 'UI模式' },
    };
    return configs[type] || { icon: <FileTextOutlined />, color: 'default', label: '其他' };
  };

  // 点击结果项
  const handleResultClick = (result: SearchResult) => {
    if (result.conversation_id) {
      navigate(`/project/${projectId}/requirement/${result.conversation_id}`);
    }
  };

  return (
    <Card>
      <Space orientation="vertical" size="large" style={{ width: '100%' }}>
        {/* 搜索输入框 */}
        <Search
          placeholder="搜索需求、模块、技术模式、UI组件..."
          size="large"
          allowClear
          enterButton={<SearchOutlined />}
          loading={searching}
          onSearch={handleSearch}
          onChange={(e) => setSearchQuery(e.target.value)}
          value={searchQuery}
        />

        {/* 筛选器 */}
        <Space wrap>
          <Space>
            <Text type="secondary">类型：</Text>
            <Select
              style={{ width: 120 }}
              placeholder="全部"
              allowClear
              value={typeFilter}
              onChange={setTypeFilter}
              options={[
                { label: '需求', value: 'requirement' },
                { label: '模块', value: 'module' },
                { label: '技术', value: 'tech' },
                { label: 'UI/UX', value: 'ui' },
              ]}
            />
          </Space>

          {availableModules.length > 0 && (
            <Space>
              <Text type="secondary">模块：</Text>
              <Select
                style={{ width: 160 }}
                placeholder="全部模块"
                allowClear
                value={moduleFilter}
                onChange={setModuleFilter}
                options={availableModules.map((m) => ({ label: m, value: m }))}
              />
            </Space>
          )}

          {(typeFilter || moduleFilter) && (
            <Button
              size="small"
              onClick={() => {
                setTypeFilter(undefined);
                setModuleFilter(undefined);
              }}
            >
              清除筛选
            </Button>
          )}
        </Space>

        {/* 搜索结果统计 */}
        {searchQuery && (
          <div>
            <Text type="secondary">
              找到 <Text strong>{total}</Text> 个结果
            </Text>
          </div>
        )}

        {/* 搜索结果列表 */}
        {searching ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="搜索中..." />
          </div>
        ) : results.length > 0 ? (
          <List
            dataSource={results}
            renderItem={(result) => {
              const typeConfig = getTypeConfig(result.type);
              return (
                <List.Item
                  key={`${result.type}-${result.title}`}
                  style={{
                    cursor: result.conversation_id ? 'pointer' : 'default',
                    padding: '16px',
                    borderRadius: '8px',
                    transition: 'background 0.2s',
                  }}
                  className="search-result-item"
                  onClick={() => handleResultClick(result)}
                  onMouseEnter={(e) => {
                    if (result.conversation_id) {
                      e.currentTarget.style.background = '#fafafa';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                  }}
                >
                  <List.Item.Meta
                    avatar={
                      <div
                        style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '8px',
                          background: `${typeConfig.color}15`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '18px',
                          color: typeConfig.color,
                        }}
                      >
                        {typeConfig.icon}
                      </div>
                    }
                    title={
                      <Space>
                        <Text strong style={{ fontSize: '15px' }}>
                          {result.title}
                        </Text>
                        <Badge
                          count={Math.round(result.relevance_score * 10) / 10}
                          style={{
                            backgroundColor: '#52c41a',
                            fontSize: '10px',
                          }}
                          title="相关度评分"
                        />
                      </Space>
                    }
                    description={
                      <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                        <Paragraph
                          ellipsis={{ rows: 2 }}
                          style={{ marginBottom: 8, color: '#666' }}
                        >
                          {result.description || result.content}
                        </Paragraph>
                        <Space wrap size={[4, 4]}>
                          {result.tags.map((tag, idx) => (
                            <Tag key={idx} color={typeConfig.color}>
                              {tag}
                            </Tag>
                          ))}
                          {result.module_name && (
                            <Tag icon={<FolderOutlined />}>{result.module_name}</Tag>
                          )}
                          {result.created_at && (
                            <Tag icon={<ClockCircleOutlined />}>
                              {new Date(result.created_at).toLocaleDateString('zh-CN')}
                            </Tag>
                          )}
                        </Space>
                      </Space>
                    }
                  />
                </List.Item>
              );
            }}
          />
        ) : searchQuery ? (
          <Empty
            description={
              <Space orientation="vertical" size="small">
                <Text type="secondary">未找到相关内容</Text>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  尝试使用不同的关键词或调整筛选条件
                </Text>
              </Space>
            }
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <SearchOutlined style={{ fontSize: '48px', color: '#d9d9d9', marginBottom: '16px' }} />
            <div>
              <Text type="secondary">输入关键词搜索知识库内容</Text>
            </div>
            <div style={{ marginTop: '8px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                支持搜索：已完成需求、功能模块、技术模式、UI组件等
              </Text>
            </div>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default KnowledgeSearch;
