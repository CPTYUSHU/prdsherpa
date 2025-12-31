# PRD 导出功能

## 功能概述

PRD 导出功能允许用户将对话历史导出为结构化的产品需求文档（PRD）。系统使用 AI 智能分析对话内容，结合项目知识库，生成专业、完整的 PRD 文档。

## 核心特性

### 1. 智能文档生成
- 🤖 **AI 驱动**：使用 Gemini 2.0 Flash 分析对话内容
- 📊 **结构化输出**：自动生成包含完整章节的 PRD
- 🎯 **上下文感知**：整合项目知识库信息

### 2. 完整的 PRD 结构
生成的 PRD 包含以下章节：

1. **需求概述**
   - 需求背景
   - 需求目标
   - 目标用户

2. **功能需求**
   - 核心功能列表
   - 功能详细描述
   - 用户流程

3. **非功能需求**
   - 性能要求
   - 安全要求
   - 兼容性要求

4. **UI/UX 设计要求**
   - 界面设计规范
   - 交互设计要点
   - 视觉设计要求

5. **技术实现建议**
   - 技术架构
   - 接口设计
   - 数据模型

6. **验收标准**
   - 功能验收标准
   - 性能验收标准

7. **附录**
   - 相关文档
   - 参考资料

### 3. 多种导出方式
- **JSON 格式**：返回 PRD 内容和元数据
- **文件下载**：直接下载 Markdown 文件

### 4. 知识库集成
- 自动包含项目的系统概览
- 引用 UI 规范和技术约定
- 确保 PRD 与项目标准一致

## API 接口

### 1. 导出为 JSON

```http
POST /api/export/conversation/{conversation_id}
```

**查询参数：**
- `include_knowledge_base` (boolean, 可选): 是否包含知识库，默认 `true`

**响应示例：**
```json
{
  "content": "# 用户登录功能需求\n\n**项目名称**：电商APP...",
  "format": "markdown",
  "filename": "用户登录功能需求_20251225_230904.md"
}
```

### 2. 下载文件

```http
GET /api/export/conversation/{conversation_id}/download
```

**查询参数：**
- `include_knowledge_base` (boolean, 可选): 是否包含知识库，默认 `true`

**响应：**
- Content-Type: `text/markdown; charset=utf-8`
- Content-Disposition: `attachment; filename*=UTF-8''...`

## 使用示例

### Python 示例

```python
import httpx
import asyncio

async def export_prd():
    async with httpx.AsyncClient() as client:
        # 导出为 JSON
        response = await client.post(
            "http://localhost:8000/api/export/conversation/{conversation_id}",
            params={"include_knowledge_base": True}
        )
        result = response.json()
        print(f"文件名: {result['filename']}")
        print(f"内容长度: {len(result['content'])} 字符")
        
        # 下载文件
        response = await client.get(
            "http://localhost:8000/api/export/conversation/{conversation_id}/download",
            params={"include_knowledge_base": True}
        )
        with open(result['filename'], 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"PRD 已保存到: {result['filename']}")

asyncio.run(export_prd())
```

### cURL 示例

```bash
# 导出为 JSON
curl -X POST "http://localhost:8000/api/export/conversation/{conversation_id}?include_knowledge_base=true" \
  -H "accept: application/json"

# 下载文件
curl -X GET "http://localhost:8000/api/export/conversation/{conversation_id}/download?include_knowledge_base=true" \
  -H "accept: text/markdown" \
  -o "prd.md"
```

## 生成的 PRD 示例

以下是一个实际生成的 PRD 片段：

```markdown
# 用户登录功能需求

**项目名称**：电商APP  
**文档版本**：1.0  
**创建日期**：2025-12-25  
**最后更新**：2025-12-25

---

## 1. 需求概述

### 1.1 需求背景

在电商APP中，用户登录功能是用户访问和使用APP各项功能的基础。
一个稳定、安全、便捷的登录功能能够提升用户体验，增加用户粘性...

### 1.2 需求目标

*   实现支持手机号和邮箱两种登录方式
*   提供记住密码和忘记密码功能
*   确保用户账号安全，防止恶意攻击
*   提供良好的用户体验，简化登录流程

### 1.3 目标用户

*   **年轻用户：** 追求便捷、快速的登录体验
*   **注重安全的用户：** 对账号安全有较高要求
...

## 2. 功能需求

### 2.1 核心功能列表

*   **手机号登录：** 用户通过手机号+验证码的方式登录
*   **邮箱登录：** 用户通过邮箱+密码的方式登录
*   **记住密码：** 用户选择记住密码后，下次登录时自动填充
*   **忘记密码：** 用户通过手机号或邮箱找回密码

### 2.2 功能详细描述

#### 2.2.1 手机号登录

*   **功能描述：** 用户输入手机号，点击"获取验证码"按钮...
*   **输入：**
    *   手机号：符合手机号格式的字符串
    *   验证码：6位数字
*   **输出：**
    *   登录成功：跳转到首页
    *   登录失败：提示错误信息
...
```

## 技术实现

### 核心服务

**ExportService** (`backend/app/services/export_service.py`)

主要方法：
- `export_conversation_to_markdown()`: 导出对话为 Markdown
- `_generate_prd_with_ai()`: 使用 AI 生成 PRD
- `_format_conversation()`: 格式化对话内容
- `_format_knowledge_base()`: 格式化知识库
- `_sanitize_filename()`: 清理文件名

### AI 提示词

系统使用精心设计的提示词指导 AI 生成专业的 PRD：

```python
prompt = f"""基于以下对话内容，生成一份结构化的产品需求文档（PRD）。

# 项目信息
- 项目名称：{project.name}
- 项目描述：{project.description}

# 知识库
{kb_context}

# 对话内容
{conversation_text}

# 要求
请生成一份完整的PRD文档，包含以下部分：
1. 需求概述
2. 功能需求
3. 非功能需求
4. UI/UX 设计要求
5. 技术实现建议
6. 验收标准
7. 附录

请使用 Markdown 格式，内容要详细、专业、可执行。
"""
```

### 文件名生成

文件名格式：`{对话标题}_{时间戳}.md`

- 自动清理无效字符（`<>:"/\|?*`）
- 限制长度（最多 50 字符）
- 添加时间戳确保唯一性
- 支持中文（UTF-8 编码）

### 编码处理

为了正确处理中文文件名和内容：

1. **内容编码**：使用 UTF-8 编码
2. **文件名编码**：使用 RFC 5987 标准（`filename*=UTF-8''...`）
3. **响应头**：明确指定 `charset=utf-8`

## 测试

运行完整的导出功能测试：

```bash
cd /Users/aiden/prdsherpa
venv/bin/python test_export.py
```

测试覆盖：
- ✅ 创建项目
- ✅ 上传和分析文件
- ✅ 构建和确认知识库
- ✅ 创建对话并发送消息
- ✅ 导出为 JSON
- ✅ 下载为文件
- ✅ 不包含知识库的导出
- ✅ 清理测试数据

## 配置

### 环境变量

确保 `.env` 文件中配置了 Gemini API：

```env
GEMINI_API_KEY=your_api_key_here
```

### AI 参数

在 `export_service.py` 中可以调整 AI 生成参数：

```python
prd_content = await self.gemini_service.generate_text(
    prompt=prompt,
    temperature=0.3,  # 较低的温度确保输出更结构化
    max_tokens=8000   # 最大 token 数
)
```

## 最佳实践

### 1. 对话质量
- 确保对话内容详细、清晰
- 包含足够的需求细节
- AI 的提问和澄清有助于生成更好的 PRD

### 2. 知识库
- 在导出前确认知识库
- 知识库信息会被整合到 PRD 中
- 包含 UI 规范和技术约定

### 3. 文件管理
- 文件名自动生成，包含时间戳
- 建议定期整理导出的 PRD 文件
- 可以使用版本控制管理 PRD

## 故障排除

### 问题 1：导出超时

**原因**：AI 生成内容时间较长

**解决方案**：
```python
async with httpx.AsyncClient(timeout=60.0) as client:
    # 增加超时时间
```

### 问题 2：中文乱码

**原因**：编码问题

**解决方案**：
- 确保使用 UTF-8 编码保存文件
- 检查响应头中的 `charset=utf-8`

### 问题 3：生成的 PRD 不完整

**原因**：对话内容不足或 AI token 限制

**解决方案**：
- 增加对话细节
- 调整 `max_tokens` 参数
- 分段导出长对话

## 未来优化

### 计划中的功能
- [ ] 支持自定义 PRD 模板
- [ ] 支持多种导出格式（PDF、Word）
- [ ] PRD 版本管理
- [ ] 导出历史记录
- [ ] 批量导出
- [ ] PRD 对比功能

### 性能优化
- [ ] 缓存生成的 PRD
- [ ] 异步生成（Celery）
- [ ] 流式输出
- [ ] 增量更新

## 总结

PRD 导出功能是 PRD助手 的核心功能之一，它将对话式需求撰写的结果转化为专业、结构化的产品需求文档。通过 AI 的智能分析和项目知识库的整合，生成的 PRD 不仅内容完整，而且符合项目标准，可以直接用于开发和评审。

**关键优势：**
- 🚀 **高效**：几秒钟生成完整 PRD
- 🎯 **准确**：基于实际对话内容
- 📚 **专业**：结构完整、格式规范
- 🔧 **灵活**：支持多种导出方式
- 🌐 **国际化**：完美支持中文

