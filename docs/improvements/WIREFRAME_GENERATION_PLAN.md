# 线框图自动生成功能 - 技术方案

> 基于 PRD 文档自动生成简单线框图原型
> 计划时间：2025-12-29

## 一、功能目标

### 核心价值
- **快速可视化**：将文字 PRD 转化为可视化的界面原型
- **降低沟通成本**：让研发、设计团队更容易理解需求
- **低保真原型**：不追求完美设计，重点展示功能布局和交互流程
- **可编辑**：生成后可以手动调整

### 使用场景
1. PM 完成 PRD 后，点击"生成线框图"按钮
2. AI 分析 PRD 内容，提取页面结构、功能布局
3. 自动生成多个页面的线框图
4. PM 可以预览、编辑、导出线框图

---

## 二、技术方案对比

### 方案 1：React 组件渲染 ⭐ 推荐
**原理**：
- AI 分析 PRD 生成结构化 JSON 数据
- 前端用 React 组件渲染成交互式线框图
- 使用简单的 CSS 样式模拟低保真效果

**优点**：
- ✅ 完全可控，样式统一
- ✅ 可交互（点击、跳转、拖拽）
- ✅ 易于编辑和调整
- ✅ 支持实时预览
- ✅ 可导出为 PNG/SVG/JSON

**缺点**：
- ❌ 需要开发 UI 组件库
- ❌ 复杂布局需要更多代码

**技术栈**：
```
后端：FastAPI + Gemini API
前端：React + Ant Design + react-grid-layout
渲染：CSS + SVG
```

---

### 方案 2：Excalidraw 集成
**原理**：
- AI 生成 Excalidraw 格式的 JSON 数据
- 使用 @excalidraw/excalidraw 库渲染
- 手绘风格的线框图

**优点**：
- ✅ 开箱即用的编辑功能
- ✅ 手绘风格，明确表示"低保真"
- ✅ 成熟的开源库
- ✅ 支持导出 PNG/SVG

**缺点**：
- ❌ AI 生成 Excalidraw JSON 比较复杂
- ❌ 样式不够专业
- ❌ 较大的依赖包

**技术栈**：
```
后端：FastAPI + Gemini API
前端：React + @excalidraw/excalidraw
```

---

### 方案 3：HTML/CSS 低保真原型
**原理**：
- AI 直接生成 HTML/CSS 代码
- 使用 iframe 或 dangerouslySetInnerHTML 渲染
- 样式使用低保真设计（灰色、线框、占位符）

**优点**：
- ✅ 实现简单快速
- ✅ AI 擅长生成 HTML/CSS
- ✅ 样式灵活

**缺点**：
- ❌ 安全风险（XSS）
- ❌ 难以编辑
- ❌ 不够结构化

---

### 方案 4：Mermaid 流程图
**原理**：
- AI 生成 Mermaid 语法
- 使用 mermaid.js 渲染流程图

**优点**：
- ✅ 适合展示页面流程
- ✅ 文本格式，易于编辑
- ✅ 轻量级

**缺点**：
- ❌ 不是真正的线框图
- ❌ 无法展示页面布局
- ❌ 样式受限

---

## 三、推荐方案：React 组件渲染

### 为什么选择方案 1？
1. **最灵活**：完全控制 UI 组件和样式
2. **最专业**：可以生成接近真实界面的线框图
3. **可扩展**：未来可以升级为高保真原型
4. **可编辑**：拖拽、调整、导出
5. **与现有技术栈契合**：已经在使用 React + Ant Design

---

## 四、详细实现方案

### 4.1 数据结构设计

#### 线框图数据模型 (JSON)

```json
{
  "wireframe_id": "uuid",
  "conversation_id": "uuid",
  "project_id": "uuid",
  "created_at": "2025-12-29T10:00:00Z",
  "pages": [
    {
      "page_id": "page_1",
      "page_name": "登录页",
      "page_type": "auth",
      "width": 375,
      "height": 812,
      "components": [
        {
          "id": "comp_1",
          "type": "header",
          "label": "欢迎登录",
          "x": 0,
          "y": 0,
          "width": 375,
          "height": 60,
          "style": {
            "backgroundColor": "#f5f5f5",
            "textAlign": "center"
          }
        },
        {
          "id": "comp_2",
          "type": "input",
          "label": "手机号",
          "placeholder": "请输入手机号",
          "x": 20,
          "y": 100,
          "width": 335,
          "height": 44
        },
        {
          "id": "comp_3",
          "type": "input",
          "label": "密码",
          "placeholder": "请输入密码",
          "input_type": "password",
          "x": 20,
          "y": 160,
          "width": 335,
          "height": 44
        },
        {
          "id": "comp_4",
          "type": "button",
          "label": "登录",
          "variant": "primary",
          "x": 20,
          "y": 240,
          "width": 335,
          "height": 44,
          "action": {
            "type": "navigate",
            "target": "page_2"
          }
        }
      ],
      "interactions": [
        {
          "from": "comp_4",
          "to": "page_2",
          "type": "click"
        }
      ]
    },
    {
      "page_id": "page_2",
      "page_name": "首页",
      "page_type": "main",
      "components": [...]
    }
  ],
  "navigation_flow": {
    "start_page": "page_1",
    "flows": [
      {
        "from": "page_1",
        "to": "page_2",
        "condition": "登录成功"
      }
    ]
  }
}
```

#### 组件类型库

```typescript
type ComponentType =
  | 'header'          // 页面标题
  | 'navbar'          // 导航栏
  | 'sidebar'         // 侧边栏
  | 'input'           // 输入框
  | 'textarea'        // 文本域
  | 'button'          // 按钮
  | 'link'            // 链接
  | 'image'           // 图片占位符
  | 'icon'            // 图标
  | 'text'            // 文本
  | 'label'           // 标签
  | 'checkbox'        // 复选框
  | 'radio'           // 单选框
  | 'select'          // 下拉选择
  | 'table'           // 表格
  | 'list'            // 列表
  | 'card'            // 卡片
  | 'tabs'            // 标签页
  | 'modal'           // 弹窗
  | 'form'            // 表单容器
  | 'container'       // 容器
  | 'divider'         // 分割线
  | 'breadcrumb'      // 面包屑
  | 'pagination'      // 分页
  | 'search'          // 搜索框
  | 'filter'          // 筛选器
  | 'chart'           // 图表占位符
  | 'avatar'          // 头像
  | 'badge';          // 徽标
```

---

### 4.2 后端实现

#### 新增服务：WireframeService

```python
# backend/app/services/wireframe_service.py

class WireframeService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def generate_wireframe(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        device_type: str = "mobile"  # mobile, tablet, desktop
    ) -> Dict[str, Any]:
        """
        根据 PRD 对话生成线框图数据

        Args:
            db: 数据库会话
            conversation_id: 对话 ID
            device_type: 设备类型（手机、平板、桌面）

        Returns:
            线框图 JSON 数据
        """
        # 1. 获取对话和消息
        conversation = await self._get_conversation(db, conversation_id)
        messages = await self._get_messages(db, conversation_id)

        # 2. 获取知识库
        knowledge_base = await self._get_knowledge_base(db, conversation.project_id)

        # 3. 构建 AI 提示词
        prompt = self._build_wireframe_prompt(
            conversation, messages, knowledge_base, device_type
        )

        # 4. 调用 AI 生成线框图数据
        wireframe_json = await self._generate_with_ai(prompt)

        # 5. 保存到数据库（可选）
        wireframe = await self._save_wireframe(db, wireframe_json)

        return wireframe_json

    def _build_wireframe_prompt(
        self,
        conversation,
        messages,
        knowledge_base,
        device_type
    ) -> str:
        """构建 AI 提示词"""

        # 设备尺寸
        device_specs = {
            "mobile": {"width": 375, "height": 812, "name": "移动端"},
            "tablet": {"width": 768, "height": 1024, "name": "平板"},
            "desktop": {"width": 1440, "height": 900, "name": "桌面端"}
        }
        spec = device_specs.get(device_type, device_specs["mobile"])

        conversation_text = self._format_messages(messages)
        kb_text = self._format_knowledge_base(knowledge_base) if knowledge_base else ""

        prompt = f"""你是一位专业的 UI/UX 设计师，请根据以下 PRD 对话内容，生成低保真线框图的结构化数据。

# 设备规格
- 设备类型：{spec['name']}
- 画布尺寸：{spec['width']} x {spec['height']} 像素

# 项目知识库
{kb_text}

# PRD 对话内容
{conversation_text}

# 任务要求
请分析 PRD 内容，提取所有需要的页面和功能，生成线框图的 JSON 数据。

## 输出格式（严格 JSON）
```json
{{
  "wireframe_id": "生成唯一ID",
  "pages": [
    {{
      "page_id": "页面唯一标识",
      "page_name": "页面名称（如：登录页、首页、列表页）",
      "page_type": "页面类型（auth/main/list/detail/form）",
      "width": {spec['width']},
      "height": {spec['height']},
      "components": [
        {{
          "id": "组件唯一标识",
          "type": "组件类型（header/input/button/text/image/list/card等）",
          "label": "组件文本标签",
          "placeholder": "占位符文本（如果是输入框）",
          "x": "X坐标（距离左边）",
          "y": "Y坐标（距离顶部）",
          "width": "组件宽度",
          "height": "组件高度",
          "style": {{
            "fontSize": "字号",
            "fontWeight": "字重",
            "color": "颜色",
            "backgroundColor": "背景色",
            "textAlign": "对齐方式"
          }},
          "action": {{
            "type": "交互类型（navigate/submit/cancel）",
            "target": "目标页面ID"
          }}
        }}
      ]
    }}
  ],
  "navigation_flow": {{
    "start_page": "起始页面ID",
    "flows": [
      {{
        "from": "源页面ID",
        "to": "目标页面ID",
        "condition": "触发条件描述"
      }}
    ]
  }}
}}
```

## 设计原则
1. **简洁明了**：只包含核心功能和关键信息
2. **低保真风格**：使用灰色调、线框、占位符
3. **功能完整**：覆盖 PRD 中提到的所有主要功能
4. **合理布局**：遵循常见的 UI 布局规范
5. **清晰层级**：页面间的导航关系要清晰

## 组件类型参考
- header: 页面标题栏
- navbar: 导航栏（顶部或底部）
- input: 输入框
- button: 按钮（primary/default/text）
- text: 文本标签
- image: 图片占位符
- list: 列表容器
- card: 卡片
- table: 表格
- form: 表单容器
- tabs: 标签页
- modal: 弹窗

## 示例参考
如果 PRD 提到"用户登录"，应该生成：
- 登录页（包含手机号输入框、密码输入框、登录按钮）
- 导航到首页的流程

请严格按照 JSON 格式输出，不要添加任何其他说明文字。
"""
        return prompt

    async def _generate_with_ai(self, prompt: str) -> Dict[str, Any]:
        """调用 AI 生成线框图数据"""
        try:
            response = await self.gemini_service.generate_text(
                prompt=prompt,
                temperature=0.3,  # 低温度，更结构化
                max_tokens=12000
            )

            # 解析 JSON（处理可能的 markdown 代码块）
            json_str = response.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            json_str = json_str.strip()

            wireframe_data = json.loads(json_str)

            # 验证数据结构
            self._validate_wireframe_data(wireframe_data)

            return wireframe_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise ValueError("AI 生成的数据格式不正确")
        except Exception as e:
            logger.error(f"Error generating wireframe with AI: {e}")
            raise

    def _validate_wireframe_data(self, data: Dict[str, Any]):
        """验证线框图数据结构"""
        required_fields = ["pages"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")

        if not isinstance(data["pages"], list) or len(data["pages"]) == 0:
            raise ValueError("至少需要一个页面")

        for page in data["pages"]:
            if "components" not in page or not isinstance(page["components"], list):
                raise ValueError(f"页面 {page.get('page_name', '未知')} 缺少组件")
```

#### 新增数据库模型（可选）

```python
# backend/app/models/wireframe.py

class Wireframe(Base):
    """线框图模型"""
    __tablename__ = "wireframes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    device_type = Column(String(20), nullable=False, default="mobile")  # mobile/tablet/desktop
    wireframe_data = Column(JSON, nullable=False)  # 线框图 JSON 数据

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系
    conversation = relationship("Conversation", back_populates="wireframes")
    project = relationship("Project", back_populates="wireframes")
```

#### 新增 API 端点

```python
# backend/app/api/wireframes.py

@router.post("/{conversation_id}/wireframe")
async def generate_wireframe(
    conversation_id: UUID,
    device_type: str = "mobile",
    db: AsyncSession = Depends(get_db)
):
    """
    生成线框图

    Args:
        conversation_id: 对话 ID
        device_type: 设备类型（mobile/tablet/desktop）

    Returns:
        线框图 JSON 数据
    """
    wireframe_service = WireframeService(gemini_service)
    wireframe_data = await wireframe_service.generate_wireframe(
        db, conversation_id, device_type
    )
    return wireframe_data

@router.get("/{conversation_id}/wireframe")
async def get_wireframe(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取已生成的线框图"""
    # 从数据库查询
    pass
```

---

### 4.3 前端实现

#### 组件结构

```
frontend/src/
├── components/
│   ├── Wireframe/
│   │   ├── WireframeCanvas.tsx        # 画布容器
│   │   ├── WireframeComponent.tsx     # 单个组件渲染器
│   │   ├── ComponentLibrary.tsx       # 组件库（用于编辑）
│   │   ├── PageNavigator.tsx          # 页面切换导航
│   │   └── WireframeToolbar.tsx       # 工具栏（缩放、导出）
│   └── WireframePreview.tsx           # 预览模式组件
└── pages/
    └── WireframeEditor.tsx             # 线框图编辑器页面
```

#### WireframeCanvas.tsx（核心组件）

```typescript
import React, { useState } from 'react';
import { Card, Spin, Button, Space } from 'antd';
import { ZoomInOutlined, ZoomOutOutlined, DownloadOutlined } from '@ant-design/icons';
import WireframeComponent from './WireframeComponent';

interface WireframeCanvasProps {
  wireframeData: any;
  editable?: boolean;
}

const WireframeCanvas: React.FC<WireframeCanvasProps> = ({
  wireframeData,
  editable = false
}) => {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [zoom, setZoom] = useState(1);

  if (!wireframeData || !wireframeData.pages) {
    return <Spin />;
  }

  const currentPage = wireframeData.pages[currentPageIndex];

  const handleZoomIn = () => setZoom(Math.min(zoom + 0.1, 2));
  const handleZoomOut = () => setZoom(Math.max(zoom - 0.1, 0.5));

  const handleExport = () => {
    // 导出为 PNG
    // 使用 html2canvas 库
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 工具栏 */}
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          {/* 页面切换 */}
          <Space>
            {wireframeData.pages.map((page: any, index: number) => (
              <Button
                key={page.page_id}
                type={currentPageIndex === index ? 'primary' : 'default'}
                onClick={() => setCurrentPageIndex(index)}
              >
                {page.page_name}
              </Button>
            ))}
          </Space>
        </Space>

        <Space>
          <Button icon={<ZoomOutOutlined />} onClick={handleZoomOut}>缩小</Button>
          <span>{Math.round(zoom * 100)}%</span>
          <Button icon={<ZoomInOutlined />} onClick={handleZoomIn}>放大</Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>导出</Button>
        </Space>
      </div>

      {/* 画布 */}
      <div style={{
        background: '#f5f5f5',
        padding: '40px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        minHeight: '600px'
      }}>
        <div
          style={{
            width: currentPage.width,
            height: currentPage.height,
            background: '#fff',
            border: '1px solid #d9d9d9',
            position: 'relative',
            transform: `scale(${zoom})`,
            transformOrigin: 'top center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}
        >
          {/* 渲染所有组件 */}
          {currentPage.components.map((component: any) => (
            <WireframeComponent
              key={component.id}
              component={component}
              editable={editable}
            />
          ))}
        </div>
      </div>

      {/* 页面流程图（可选） */}
      {wireframeData.navigation_flow && (
        <div style={{ marginTop: '24px' }}>
          <Card title="页面流程">
            {/* 使用 ReactFlow 或简单的流程图 */}
          </Card>
        </div>
      )}
    </div>
  );
};

export default WireframeCanvas;
```

#### WireframeComponent.tsx（组件渲染器）

```typescript
import React from 'react';
import { Input, Button } from 'antd';

interface ComponentProps {
  component: any;
  editable?: boolean;
}

const WireframeComponent: React.FC<ComponentProps> = ({ component, editable }) => {
  const baseStyle: React.CSSProperties = {
    position: 'absolute',
    left: component.x,
    top: component.y,
    width: component.width,
    height: component.height,
    ...component.style,
  };

  // 低保真样式
  const wireframeStyle: React.CSSProperties = {
    border: '1px solid #d9d9d9',
    borderRadius: '4px',
    backgroundColor: '#fafafa',
  };

  // 根据组件类型渲染不同的 UI
  switch (component.type) {
    case 'header':
      return (
        <div style={{
          ...baseStyle,
          ...wireframeStyle,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '18px',
          fontWeight: 'bold',
          backgroundColor: '#f0f0f0'
        }}>
          {component.label}
        </div>
      );

    case 'input':
      return (
        <div style={baseStyle}>
          {component.label && (
            <div style={{ marginBottom: '4px', fontSize: '12px', color: '#666' }}>
              {component.label}
            </div>
          )}
          <Input
            placeholder={component.placeholder}
            disabled={!editable}
            style={{
              border: '2px dashed #d9d9d9',
              backgroundColor: '#fafafa'
            }}
          />
        </div>
      );

    case 'button':
      return (
        <div style={baseStyle}>
          <Button
            type={component.variant === 'primary' ? 'primary' : 'default'}
            block
            style={{ height: '100%' }}
          >
            {component.label}
          </Button>
        </div>
      );

    case 'text':
      return (
        <div style={{
          ...baseStyle,
          fontSize: component.style?.fontSize || '14px',
          color: component.style?.color || '#333'
        }}>
          {component.label}
        </div>
      );

    case 'image':
      return (
        <div style={{
          ...baseStyle,
          ...wireframeStyle,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#999',
          fontSize: '12px'
        }}>
          [图片]
        </div>
      );

    case 'list':
      return (
        <div style={{
          ...baseStyle,
          ...wireframeStyle,
          padding: '8px',
          overflowY: 'auto'
        }}>
          {/* 渲染列表项 */}
          {[1, 2, 3].map(i => (
            <div key={i} style={{
              padding: '12px',
              borderBottom: '1px solid #f0f0f0',
              backgroundColor: '#fff',
              marginBottom: '4px'
            }}>
              列表项 {i}
            </div>
          ))}
        </div>
      );

    case 'card':
      return (
        <div style={{
          ...baseStyle,
          ...wireframeStyle,
          padding: '12px',
          backgroundColor: '#fff'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
            {component.label}
          </div>
          <div style={{ color: '#999', fontSize: '12px' }}>
            卡片内容区域
          </div>
        </div>
      );

    default:
      return (
        <div style={{
          ...baseStyle,
          ...wireframeStyle,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          color: '#999'
        }}>
          {component.type}: {component.label}
        </div>
      );
  }
};

export default WireframeComponent;
```

---

### 4.4 集成到现有功能

#### 在 Chat.tsx 中添加"生成线框图"按钮

```typescript
// 在导出按钮旁边添加
<Button
  icon={<LayoutOutlined />}
  onClick={handleGenerateWireframe}
  loading={generatingWireframe}
  disabled={messages.length === 0}
>
  生成线框图
</Button>

const handleGenerateWireframe = async () => {
  if (!conversation) return;
  try {
    setGeneratingWireframe(true);
    const wireframeData = await wireframeApi.generate(conversation.id, 'mobile');
    // 跳转到线框图预览页面
    navigate(`/project/${projectId}/wireframe/${conversation.id}`);
  } catch (error) {
    message.error('生成线框图失败');
  } finally {
    setGeneratingWireframe(false);
  }
};
```

---

## 五、实施计划

### Phase 1：后端基础（3天）
- [ ] 创建 `WireframeService`
- [ ] 设计 AI 提示词模板
- [ ] 实现 JSON 生成和验证
- [ ] 添加 API 端点
- [ ] 测试 AI 生成质量

### Phase 2：前端渲染（3天）
- [ ] 创建 `WireframeCanvas` 组件
- [ ] 实现 `WireframeComponent` 渲染器
- [ ] 支持所有基础组件类型
- [ ] 添加缩放和导航功能
- [ ] 集成到 Chat 页面

### Phase 3：增强功能（2天）
- [ ] 添加导出功能（PNG/SVG）
- [ ] 实现页面流程图展示
- [ ] 优化 AI 提示词
- [ ] 添加设备类型切换

### Phase 4：可选增强（后续）
- [ ] 拖拽编辑功能
- [ ] 组件库扩展
- [ ] 版本历史
- [ ] 协作编辑

---

## 六、成功指标

### MVP 目标
1. ✅ 能够根据 PRD 生成 2-5 个页面的线框图
2. ✅ 支持 15+ 种常见组件类型
3. ✅ 页面布局合理、美观
4. ✅ 支持预览和导出

### 质量指标
- AI 生成成功率 > 80%
- 生成时间 < 30 秒
- 用户满意度 > 4/5

---

## 七、风险和挑战

### 技术风险
1. **AI 生成质量不稳定**
   - 缓解：优化提示词，提供更多示例
   - 缓解：添加数据验证和修正逻辑

2. **复杂布局难以生成**
   - 缓解：从简单页面开始，逐步支持复杂布局
   - 缓解：提供手动编辑功能

3. **性能问题**
   - 缓解：优化组件渲染
   - 缓解：使用虚拟滚动

### 产品风险
1. **用户期望过高**
   - 缓解：明确说明是"低保真"原型
   - 缓解：提供编辑功能

---

## 八、替代方案

如果 React 组件方案过于复杂，可以考虑：

### 备选方案：使用 Excalidraw
- 更快实现
- 手绘风格更明确表示"低保真"
- 现成的编辑功能

### 备选方案：纯 HTML/CSS
- 最简单的实现
- 可以直接在浏览器中预览
- 安全性需要注意

---

## 九、总结

推荐使用 **React 组件渲染方案**，因为：
1. 与现有技术栈完美契合
2. 最灵活、可扩展
3. 提供最好的用户体验
4. 未来可以升级为高保真原型工具

实施顺序：
1. 先完成后端 AI 生成（3天）
2. 再完成前端渲染（3天）
3. 最后优化和增强（2天）

预计 **8个工作日** 可以完成 MVP 版本。
