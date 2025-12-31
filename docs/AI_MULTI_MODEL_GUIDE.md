# AI 多模型支持使用指南

> 更新时间: 2025-12-29
> 版本: 1.0

## 📋 功能概述

PRD Sherpa 现在支持多个AI模型提供商，包括：
- **Google Gemini** (gemini-3-flash-preview) - 默认，免费
- **OpenAI GPT-4** (gpt-4-turbo-preview) - 高质量，付费
- **Anthropic Claude** (claude-3-5-sonnet-20241022) - 卓越推理能力，付费

### ✨ 新功能

1. **多模型支持** - 在 Gemini、GPT-4、Claude 之间自由切换
2. **成本追踪** - 实时统计每个模型的 Token 使用量和成本
3. **上下文增强** - 对话上下文从 10 条消息增加到 50 条
4. **模型对比** - 比较不同模型的特点和定价

---

## 🚀 快速开始

### 1. 配置 API 密钥

编辑 `.env` 文件，添加以下配置：

```env
# Gemini（已有，必需）
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3-flash-preview

# OpenAI（可选）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Claude（可选）
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# 默认使用的 AI 提供商
DEFAULT_AI_PROVIDER=gemini
```

### 2. 安装依赖

如果还没安装，运行：

```bash
pip install -r requirements.txt
```

所需的包已经包含在 requirements.txt 中：
- `openai>=1.59.8`
- `anthropic>=0.42.0`
- `google-generativeai`

### 3. 重启后端服务

```bash
# 激活虚拟环境
source venv/bin/activate

# 重启服务器
python -m backend.app.main
```

---

## 📖 API 使用说明

### 查看可用模型

**GET** `/api/ai/providers`

```bash
curl http://localhost:8000/api/ai/providers
```

**响应示例：**
```json
{
  "providers": [
    {
      "name": "gemini",
      "available": true,
      "model": "gemini-3-flash-preview",
      "supports_streaming": true,
      "supports_images": true,
      "current": true
    },
    {
      "name": "openai",
      "available": true,
      "model": "gpt-4-turbo-preview",
      "supports_streaming": true,
      "supports_images": true,
      "current": false
    },
    {
      "name": "claude",
      "available": false,
      "model": "claude-3-5-sonnet-20241022",
      "supports_streaming": true,
      "supports_images": true,
      "current": false
    }
  ],
  "current_provider": "gemini"
}
```

### 切换 AI 模型

**POST** `/api/ai/provider/select`

```bash
# 切换到 GPT-4
curl -X POST http://localhost:8000/api/ai/provider/select \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai"}'

# 切换到 Claude
curl -X POST http://localhost:8000/api/ai/provider/select \
  -H "Content-Type: application/json" \
  -d '{"provider": "claude"}'

# 切换回 Gemini
curl -X POST http://localhost:8000/api/ai/provider/select \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini"}'
```

**响应示例：**
```json
{
  "provider": "openai",
  "model_name": "gpt-4-turbo-preview",
  "success": true,
  "message": "Successfully switched to openai (gpt-4-turbo-preview)"
}
```

### 查看当前模型

**GET** `/api/ai/provider/current`

```bash
curl http://localhost:8000/api/ai/provider/current
```

**响应示例：**
```json
{
  "provider": "openai",
  "model_name": "gpt-4-turbo-preview",
  "provider_name": "OpenAI"
}
```

### 查看成本统计

**GET** `/api/ai/usage/stats`

```bash
curl http://localhost:8000/api/ai/usage/stats
```

**响应示例：**
```json
{
  "total_cost": 0.156,
  "total_tokens": 12450,
  "by_provider": {
    "gemini": {
      "cost": 0.0,
      "tokens": 5000,
      "model": "gemini-3-flash-preview"
    },
    "openai": {
      "cost": 0.156,
      "tokens": 7450,
      "model": "gpt-4-turbo-preview"
    }
  }
}
```

### 模型对比

**GET** `/api/ai/models/compare`

```bash
curl http://localhost:8000/api/ai/models/compare
```

返回各模型的详细对比信息。

---

## 💰 成本预估

### Gemini 3 Flash Preview
- **成本**: 免费（免费额度内）
- **优势**: 速度快，支持中文，多模态
- **最适合**: 日常使用、原型开发、预算有限

### OpenAI GPT-4 Turbo
- **输入**: $0.01 / 1K tokens
- **输出**: $0.03 / 1K tokens
- **优势**: 高质量输出，最新功能
- **最适合**: 重要PRD、复杂需求分析

### Claude 3.5 Sonnet
- **输入**: $0.003 / 1K tokens
- **输出**: $0.015 / 1K tokens
- **优势**: 卓越推理能力，超长上下文(200K)
- **最适合**: 复杂逻辑、代码相关PRD

### 成本示例

假设一次对话使用 2000 input tokens 和 1500 output tokens：

| 模型 | 输入成本 | 输出成本 | 总成本 |
|------|---------|---------|--------|
| Gemini | $0.00 | $0.00 | **$0.00** |
| GPT-4 Turbo | $0.02 | $0.045 | **$0.065** |
| Claude 3.5 | $0.006 | $0.0225 | **$0.0285** |

---

## 🎯 使用建议

### 何时使用 Gemini
- ✅ 日常PRD编写
- ✅ 快速原型验证
- ✅ 预算有限
- ✅ 中文内容处理
- ✅ 需要图片分析

### 何时使用 GPT-4
- ✅ 重要的商业PRD
- ✅ 需要最新功能
- ✅ 对质量要求极高
- ✅ 复杂的英文内容

### 何时使用 Claude
- ✅ 技术型PRD（含代码）
- ✅ 需要深度推理
- ✅ 超长文档分析
- ✅ 成本效益平衡

---

## 🔧 技术架构

### 核心组件

1. **AIServiceBase** (`backend/app/services/ai_service_base.py`)
   - 抽象基类，定义统一接口
   - 成本追踪、使用统计

2. **AI Service Factory** (`backend/app/services/ai_service_factory.py`)
   - 单例模式管理服务实例
   - 模型切换、缓存管理

3. **具体实现**
   - `GeminiService` - Google Gemini API
   - `OpenAIService` - OpenAI GPT-4 API
   - `ClaudeService` - Anthropic Claude API

### 核心接口

所有AI服务实现以下统一接口：

```python
async def generate_text(prompt: str, ...) -> str
async def chat(messages: List[AIMessage], ...) -> str
async def chat_stream(messages: List[AIMessage], ...) -> AsyncGenerator[str, None]
async def analyze_document(content: str, ...) -> Dict[str, Any]
async def analyze_image(image_path: str, ...) -> Dict[str, Any]
def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float
```

---

## 📈 上下文增强

### 变更说明

对话上下文长度已从 **10 条消息** 增加到 **50 条消息**。

**影响：**
- ✅ AI 可以引用更长的对话历史
- ✅ 更连贯和上下文感知的响应
- ✅ 更好地理解需求演进过程
- ⚠️ 略微增加 API 成本（更多 input tokens）

**位置：** `backend/app/services/conversation_service.py:27`

---

## ⚠️ 注意事项

### 1. API 密钥安全
- 永远不要将 API 密钥提交到 Git
- 使用 `.env` 文件存储密钥
- `.env` 已在 `.gitignore` 中

### 2. 成本控制
- 定期检查 `/api/ai/usage/stats` 监控成本
- Gemini 免费额度用完后会产生费用
- GPT-4 和 Claude 从第一次调用就开始计费

### 3. 模型限制
- 不同模型的 max_tokens 限制不同
- Gemini: 32K, GPT-4: 128K, Claude: 200K
- 超长文档可能被截断

### 4. 错误处理
- 如果 API 密钥无效，会返回 400 错误
- 切换到未配置的provider会失败
- 建议在生产环境始终配置备用模型

---

## 🔮 未来计划

- [ ] 前端 UI 集成模型选择器
- [ ] 智能推荐服务（根据需求自动选择最佳模型）
- [ ] 模型性能对比工具
- [ ] 自定义模型参数（temperature, max_tokens）
- [ ] 模型组合（使用不同模型处理不同任务）
- [ ] 本地模型支持（Ollama集成）

---

## 📞 问题反馈

如有问题或建议，请在 GitHub Issues 中提出。

**相关文档：**
- [CLAUDE.md](../CLAUDE.md) - 项目总体说明
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - 快速参考指南

---

**享受多模型带来的灵活性！** 🚀
