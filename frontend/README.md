# PRD助手 Frontend

React + TypeScript + Vite 前端应用，提供现代化的 PRD 写作界面。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI 组件库**: Ant Design 5
- **状态管理**: React Context + Hooks
- **HTTP 客户端**: Axios
- **Markdown 渲染**: react-markdown + remark-gfm
- **路由**: React Router 6
- **样式**: Tailwind CSS + Ant Design
- **时间处理**: dayjs

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建 `.env.local` 文件（可选）：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 项目结构

```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── ChatInterface.tsx
│   │   └── Sidebar.tsx
│   ├── pages/               # 页面组件
│   │   ├── WelcomePage.tsx
│   │   ├── NewProjectPage.tsx
│   │   ├── KnowledgeBasePage.tsx
│   │   └── ChatPage.tsx
│   ├── contexts/            # 状态管理
│   │   └── AppContext.tsx
│   ├── services/            # API 服务
│   │   └── api.ts
│   ├── types/               # TypeScript 类型
│   │   └── index.ts
│   ├── App.tsx              # 主应用组件
│   ├── App.css              # 全局样式
│   └── main.tsx             # 应用入口
├── public/                  # 静态资源
├── index.html               # HTML 模板
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 页面路由

```
/                           - 欢迎页
/project/new                - 新建项目
/project/:id/kb             - 知识库确认
/project/:id/chat           - 对话写需求
/project/:id/chat/:convId   - 特定对话
```

## 核心功能

### 1. 项目管理
- 创建新项目
- 项目列表展示
- 项目切换

### 2. 文件上传
- 拖拽上传
- 多文件上传
- 文件列表管理
- AI 自动分析

### 3. 知识库
- 结构化展示
- 在线编辑
- 确认流程

### 4. 对话界面
- 实时对话
- Markdown 渲染
- 对话历史
- 自动生成标题

### 5. PRD 导出
- 预览 PRD
- 下载 Markdown 文件

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `App.tsx` 添加路由
3. 在 `Sidebar.tsx` 添加导航（如需要）

### 添加新 API

1. 在 `src/services/api.ts` 添加 API 方法
2. 在组件中使用 API

### 样式开发

- 优先使用 Ant Design 组件
- 使用 Tailwind CSS 工具类
- 自定义样式写在 `App.css`

## 可用脚本

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | 后端 API 地址 | `http://localhost:8000` |

## 完整文档

查看项目根目录的文档中心获取完整文档：

- [文档中心](../docs/README.md) - 所有文档导航
- [前端开发总结](../docs/reports/FRONTEND_COMPLETE.md) - 前端功能完成情况
- [快速开始指南](../docs/guides/QUICKSTART.md) - 完整使用指南

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 常见问题

### Q: API 请求失败

A: 检查后端服务是否启动，确认 `VITE_API_BASE_URL` 配置正确。

### Q: 样式不生效

A: 确保 Tailwind CSS 配置正确，重启开发服务器。

### Q: 构建失败

A: 清理 `node_modules` 和 `dist`，重新安装依赖。

```bash
rm -rf node_modules dist
npm install
npm run build
```

## 贡献

欢迎贡献代码！请遵循项目的代码规范和提交规范。

---

Made with ❤️ by PRD助手 Team
