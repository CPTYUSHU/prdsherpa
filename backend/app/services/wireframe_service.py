"""
Wireframe generation service for creating low-fidelity prototypes from PRD conversations.
"""
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.conversation import Conversation, Message
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.project import Project
from backend.app.models.file import UploadedFile
from backend.app.services.gemini_service import GeminiService
import os

logger = logging.getLogger(__name__)


class WireframeService:
    """Service for generating HTML/CSS wireframes from PRD conversations."""

    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def generate_wireframe_html(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        device_type: str = "mobile",
        reference_file_ids: list[str] = None
    ) -> str:
        """
        Generate HTML/CSS wireframe from PRD conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            device_type: Device type (mobile/tablet/desktop)

        Returns:
            Complete HTML document with inline CSS
        """
        # Get conversation and messages
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Get project
        project_result = await db.execute(
            select(Project).where(Project.id == conversation.project_id)
        )
        project = project_result.scalar_one()

        # Get messages
        messages_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence)
        )
        messages = messages_result.scalars().all()

        # Get knowledge base if available
        kb_result = await db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.project_id == conversation.project_id)
            .where(KnowledgeBase.status == "confirmed")
        )
        knowledge_base = kb_result.scalar_one_or_none()

        # Get reference images if provided
        reference_image_paths = []
        if reference_file_ids:
            logger.info(f"Processing {len(reference_file_ids)} reference files")
            for file_id in reference_file_ids:
                try:
                    file_result = await db.execute(
                        select(UploadedFile).where(UploadedFile.id == UUID(file_id))
                    )
                    uploaded_file = file_result.scalar_one_or_none()
                    if uploaded_file and uploaded_file.file_type == "image":
                        file_path = uploaded_file.file_path
                        if os.path.exists(file_path):
                            reference_image_paths.append(file_path)
                            logger.info(f"Added reference image: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to load reference file {file_id}: {e}")

        # Build prompt
        prompt = self._build_wireframe_prompt(
            project=project,
            conversation=conversation,
            messages=messages,
            knowledge_base=knowledge_base,
            device_type=device_type,
            has_reference_images=len(reference_image_paths) > 0
        )

        # Generate HTML with AI (with reference images if available)
        if reference_image_paths:
            logger.info(f"Generating wireframe with {len(reference_image_paths)} reference images")
            # Use chat method with images for multimodal analysis
            chat_messages = [
                {"role": "user", "content": prompt}
            ]
            html_content = await self.gemini_service.chat(
                messages=chat_messages,
                image_paths=reference_image_paths,
                temperature=0.3,
                max_tokens=12000
            )
        else:
            # No reference images, use regular text generation
            html_content = await self.gemini_service.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=12000
            )

        # Clean up the response (remove markdown code blocks if any)
        html_content = self._clean_html_response(html_content)

        logger.info(f"Generated wireframe for conversation {conversation_id}")

        return html_content

    def _build_wireframe_prompt(
        self,
        project: Project,
        conversation: Conversation,
        messages: list,
        knowledge_base: Optional[KnowledgeBase],
        device_type: str,
        has_reference_images: bool = False
    ) -> str:
        """Build the AI prompt for wireframe generation."""

        # Device specifications
        device_specs = {
            "mobile": {"width": 375, "name": "移动端（手机）"},
            "tablet": {"width": 768, "name": "平板（iPad）"},
            "desktop": {"width": 1200, "name": "桌面端（PC）"}
        }
        spec = device_specs.get(device_type, device_specs["mobile"])

        # Format conversation
        conversation_text = self._format_messages(messages)

        # Format knowledge base
        kb_text = ""
        if knowledge_base:
            kb_text = self._format_knowledge_base(knowledge_base)

        # Base prompt with reference image support
        reference_instruction = ""
        if has_reference_images:
            reference_instruction = """
## 📸 参考截图说明
我已经为你提供了现有系统/CMS平台的截图作为参考。

**重要任务**：
1. **仔细分析参考截图**：
   - 整体布局结构（顶部导航、侧边栏、主内容区）
   - UI 组件样式（按钮、输入框、表格、卡片）
   - 配色方案和视觉风格
   - 页面层次和信息架构
   - 交互元素的位置和排列

2. **模仿参考截图的设计**：
   - 保持**相同的布局结构**（如果有侧边栏就保留侧边栏）
   - 使用**相似的组件样式**（按钮形状、输入框样式、表格风格）
   - 参考**相同的配色**（主色、辅色、背景色）
   - 复制**类似的交互模式**（导航方式、操作按钮位置）

3. **高保真原型**：
   - 生成的原型应该**看起来像**参考截图的低保真版本
   - 保留关键的视觉特征，让开发能清楚知道**在哪个位置开发新功能**
   - 不要创建全新的设计，而是**基于现有界面扩展**

4. **功能定位**：
   - 明确指出新功能应该**添加在哪里**（例如："在左侧导航栏添加'会员管理'菜单项"）
   - 使用注释标注：`<!-- 🔴 新功能：在此处添加XXX -->`
   - 保持与现有界面的一致性

**输出要求**：
- 参考截图的整体布局和风格
- 新功能与现有界面融合
- 明确标注新功能的位置
"""
        else:
            reference_instruction = """
## ⚠️ 无参考截图
由于没有提供现有系统的截图，请生成标准的低保真原型。
"""

        prompt = f"""你是一位专业的前端工程师和 UI 设计师，请根据以下 PRD 对话内容{'和提供的参考截图' if has_reference_images else ''}，生成**{'高保真' if has_reference_images else '低保真'}可视化线框图** HTML/CSS 代码。

{reference_instruction}

⚠️ **重要提示**：
- 你必须生成**带有真实 UI 控件的可视化界面**（输入框、按钮、卡片等）
- **绝对不能**只生成纯文字列表或表格
- 每个功能都要用对应的 UI 组件渲染出来（如：登录 → 输入框+按钮）

# 项目信息
- 项目名称：{project.name}
- 项目描述：{project.description or '无'}
- 设备类型：{spec['name']}
- 画布宽度：{spec['width']}px

# 项目知识库
{kb_text if kb_text else '无项目知识库'}

# PRD 对话内容
{conversation_text}

# ❌ 错误示例（绝对不能这样生成）
```html
<!-- 这是错误的！只有文字列表，没有可视化界面 -->
<div>
  <h3>WiFi Library Management</h3>
  <ul>
    <li>Content List (Happenings)</li>
    <li>Edit Content (WiFi Config)</li>
    <li>WiFi Library (System Management)</li>
  </ul>
  <button>+ Add New Zone</button>
</div>
```

# ✅ 正确示例（必须这样生成）
```html
<!-- 这是正确的！有真实的可视化 UI 组件 -->
<div class="page">
  <div class="page-header">WiFi 管理系统</div>

  <div class="tabs">
    <div class="tab active">内容列表</div>
    <div class="tab">编辑配置</div>
    <div class="tab">系统管理</div>
  </div>

  <div class="toolbar">
    <input type="text" class="input" placeholder="搜索标题..." />
    <button class="btn btn-primary">+ 新建区域</button>
  </div>

  <div class="table-container">
    <div class="table-row header">
      <div>区域名称</div>
      <div>SSID</div>
      <div>描述</div>
      <div>操作</div>
    </div>
    <div class="table-row">
      <div>Grand Lisboa Palace</div>
      <div>GLP-Guest, GLP-VIP</div>
      <div>主要酒店区域</div>
      <div>
        <button class="btn">编辑</button>
        <button class="btn">删除</button>
      </div>
    </div>
  </div>
</div>
```

# 任务要求
请生成一个完整的、响应式的、低保真风格的 HTML 页面，要求如下：

## 1. 整体结构
- 生成完整的 HTML5 文档（包含 <!DOCTYPE html>、<html>、<head>、<body>）
- 所有样式写在 <style> 标签内（内联 CSS）
- 支持多个页面，使用 Tab 标签页或按钮进行切换
- 默认显示第一个页面

## 2. 低保真设计风格
**颜色方案：**
- 背景色：#ffffff（页面）、#f5f5f5（容器）
- 边框色：#d9d9d9（实线）、#999999（虚线）
- 文字色：#333333（主要）、#666666（次要）、#999999（辅助）
- 主色调：#1890ff（按钮、链接）

**视觉风格：**
- 使用虚线边框表示输入框和占位区域：border: 2px dashed #d9d9d9
- 使用灰色背景表示容器和区域：background: #f5f5f5
- 图片用 [图片] 文字占位符，带虚线边框
- 图标用 [图标] 文字占位符
- 按钮使用实色背景

**布局原则：**
- 简洁明了，不要过度设计
- 合理的间距和留白（padding: 12px-20px, margin: 12px-20px）
- 清晰的层次结构
- 符合常见的 UI 布局规范

## 3. 页面组件示例

### 页面容器
```css
.page {{
    width: {spec['width']}px;
    max-width: 100%;
    margin: 0 auto;
    padding: 20px;
    background: #fff;
}}
```

### 页面头部
```css
.page-header {{
    padding: 16px;
    background: #f5f5f5;
    border-bottom: 2px solid #d9d9d9;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
}}
```

### 输入框
```css
.input-group {{
    margin-bottom: 16px;
}}
.input-label {{
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #666;
}}
.input {{
    width: 100%;
    padding: 12px;
    border: 2px dashed #d9d9d9;
    background: #fafafa;
    font-size: 14px;
    box-sizing: border-box;
}}
```

### 按钮
```css
.btn {{
    padding: 12px 24px;
    font-size: 14px;
    border: none;
    cursor: pointer;
    border-radius: 4px;
}}
.btn-primary {{
    background: #1890ff;
    color: white;
}}
.btn-default {{
    background: #f5f5f5;
    color: #333;
    border: 1px solid #d9d9d9;
}}
```

### 列表/卡片
```css
.card {{
    padding: 16px;
    background: #fff;
    border: 1px solid #d9d9d9;
    margin-bottom: 12px;
}}
.list-item {{
    padding: 12px;
    border-bottom: 1px solid #f0f0f0;
}}
```

### 图片占位符
```css
.image-placeholder {{
    width: 100%;
    height: 200px;
    border: 2px dashed #d9d9d9;
    background: #fafafa;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 14px;
}}
```

## 4. 页面切换功能
使用 JavaScript 实现页面切换：
```javascript
function showPage(pageId) {{
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {{
        page.style.display = 'none';
    }});
    document.getElementById(pageId).style.display = 'block';

    // 更新标签页样式
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {{
        tab.classList.remove('active');
    }});
    event.target.classList.add('active');
}}
```

## 5. 根据 PRD 内容生成页面
请仔细分析 PRD 对话内容，提取以下信息：
- 需要哪些页面（登录页、首页、列表页、详情页、表单页等）
- 每个页面有哪些功能模块
- 页面之间的导航关系
- 关键的交互元素（按钮、输入框、列表等）

## 6. 完整示例：登录页面
以下是一个完整的登录页 HTML 示例，请参考这个风格生成：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录页面 - 低保真原型</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}

        .page {{
            max-width: 375px;
            margin: 40px auto;
            background: #fff;
            border: 1px solid #d9d9d9;
            padding: 0;
        }}

        .page-header {{
            padding: 20px;
            background: #f5f5f5;
            border-bottom: 2px solid #d9d9d9;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
        }}

        .page-content {{
            padding: 24px;
        }}

        .logo-placeholder {{
            width: 120px;
            height: 120px;
            margin: 0 auto 24px;
            border: 2px dashed #d9d9d9;
            background: #fafafa;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 14px;
        }}

        .input-group {{
            margin-bottom: 20px;
        }}

        .input-label {{
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }}

        .input {{
            width: 100%;
            padding: 12px 16px;
            border: 2px dashed #d9d9d9;
            background: #fafafa;
            font-size: 14px;
            color: #333;
        }}

        .btn {{
            width: 100%;
            padding: 14px;
            font-size: 15px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
            font-weight: 500;
        }}

        .btn-primary {{
            background: #1890ff;
            color: white;
            margin-top: 24px;
        }}

        .link {{
            display: block;
            text-align: center;
            margin-top: 16px;
            font-size: 13px;
            color: #1890ff;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="page-header">用户登录</div>
        <div class="page-content">
            <div class="logo-placeholder">[Logo图标]</div>

            <div class="input-group">
                <label class="input-label">手机号</label>
                <input type="text" class="input" placeholder="请输入手机号" />
            </div>

            <div class="input-group">
                <label class="input-label">密码</label>
                <input type="password" class="input" placeholder="请输入密码" />
            </div>

            <button class="btn btn-primary">登录</button>

            <a href="#" class="link">忘记密码？</a>
            <a href="#" class="link">新用户注册</a>
        </div>
    </div>
</body>
</html>
```

## 7. 输出格式
请严格按照上面的示例风格，生成完整的 HTML 文档：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{conversation.title or '线框图原型'} - 低保真原型</title>
    <style>
        /* 全局样式 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}

        /* 标签页导航 */
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            background: #fff;
            padding: 12px;
            border: 1px solid #d9d9d9;
        }}
        .tab {{
            padding: 8px 16px;
            background: #f5f5f5;
            border: 1px solid #d9d9d9;
            cursor: pointer;
            font-size: 14px;
        }}
        .tab.active {{
            background: #1890ff;
            color: white;
            border-color: #1890ff;
        }}

        /* 页面容器 */
        .page {{
            display: none;
            background: #fff;
            border: 1px solid #d9d9d9;
            padding: 20px;
            max-width: {spec['width']}px;
            margin: 0 auto;
        }}
        .page.active {{
            display: block;
        }}

        /* 在这里添加更多样式... */
    </style>
</head>
<body>
    <!-- 标签页导航 -->
    <div class="tabs">
        <div class="tab active" onclick="showPage('page1')">页面1名称</div>
        <div class="tab" onclick="showPage('page2')">页面2名称</div>
        <!-- 更多标签页... -->
    </div>

    <!-- 页面1 -->
    <div id="page1" class="page active">
        <div class="page-header">页面1标题</div>
        <!-- 页面内容... -->
    </div>

    <!-- 页面2 -->
    <div id="page2" class="page">
        <div class="page-header">页面2标题</div>
        <!-- 页面内容... -->
    </div>

    <!-- 更多页面... -->

    <script>
        function showPage(pageId) {{
            // 隐藏所有页面
            const pages = document.querySelectorAll('.page');
            pages.forEach(page => page.classList.remove('active'));

            // 显示目标页面
            document.getElementById(pageId).classList.add('active');

            // 更新标签页样式
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
```

## 8. 质量检查清单
生成完成后，请确保符合以下所有要求：
- ✅ 每个功能都用**真实的 UI 组件**呈现（输入框、按钮、卡片等）
- ✅ **绝对没有**纯文字列表或简单的 <ul><li> 堆砌
- ✅ 所有输入框都有虚线边框（border: 2px dashed #d9d9d9）
- ✅ 所有占位区域都有灰色背景（background: #fafafa）
- ✅ 按钮有明显的样式和背景色
- ✅ 页面有清晰的结构和层次
- ✅ 多个页面时有标签页切换功能
- ✅ 代码完整，可以直接在浏览器运行

**重要提示：**
1. 只输出 HTML 代码，不要添加任何解释性文字
2. 确保代码完整、可直接在浏览器中运行
3. 所有页面都要根据 PRD 内容实际生成，不要使用占位文本
4. 保持低保真风格，使用虚线边框和灰色系配色
5. 必须生成**可视化界面**，而不是文字描述

请开始生成完整的 HTML 代码：
"""

        return prompt

    def _format_messages(self, messages: list) -> str:
        """Format conversation messages as text."""
        lines = []
        for msg in messages:
            role = "产品经理" if msg.role == "user" else "AI助手"
            lines.append(f"**{role}**：{msg.content}\n")
        return "\n".join(lines)

    def _format_knowledge_base(self, kb: KnowledgeBase) -> str:
        """Format knowledge base as text."""
        data = kb.structured_data
        lines = []

        # Extract key information from knowledge base
        if data.get("project_overview"):
            overview = data["project_overview"]
            lines.append("## 项目概览")
            if overview.get("product_type"):
                lines.append(f"- 产品类型：{overview['product_type']}")
            if overview.get("target_users"):
                lines.append(f"- 目标用户：{overview['target_users']}")
            lines.append("")

        if data.get("ui_ux_design"):
            ui = data["ui_ux_design"]
            lines.append("## UI/UX 设计")
            if ui.get("design_system"):
                lines.append(f"- 设计系统：{ui['design_system']}")
            if ui.get("color_scheme"):
                lines.append(f"- 配色方案：{ui['color_scheme']}")
            lines.append("")

        return "\n".join(lines)

    def _clean_html_response(self, html_content: str) -> str:
        """
        Clean AI response by removing markdown code blocks.

        Args:
            html_content: Raw AI response

        Returns:
            Cleaned HTML content
        """
        html_content = html_content.strip()

        # Remove markdown code blocks
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        elif html_content.startswith('```'):
            html_content = html_content[3:]

        if html_content.endswith('```'):
            html_content = html_content[:-3]

        return html_content.strip()
