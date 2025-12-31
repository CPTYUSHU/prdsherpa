# 项目文件组织说明

本文档说明 PRD Sherpa 项目的文件组织结构和管理规范。

## 📁 目录结构

```
prdsherpa/
├── backend/                    # 后端代码
│   ├── app/                    # FastAPI 应用
│   │   ├── api/                # API 路由
│   │   ├── core/               # 核心配置
│   │   ├── models/             # 数据库模型
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # 业务逻辑
│   │   └── main.py             # 应用入口
│   ├── alembic/                # 数据库迁移
│   ├── init_db.py              # 数据库初始化
│   ├── test_api.py             # API 测试
│   ├── requirements.txt        # 后端依赖
│   └── README.md               # 后端文档
│
├── frontend/                   # 前端代码
│   ├── src/                    # 源代码
│   │   ├── components/         # React 组件
│   │   ├── pages/              # 页面组件
│   │   ├── contexts/           # 状态管理
│   │   ├── services/           # API 服务
│   │   └── types/              # TypeScript 类型
│   ├── public/                 # 静态资源
│   ├── package.json            # 前端依赖
│   └── README.md               # 前端文档
│
├── docs/                       # 📚 文档中心
│   ├── README.md               # 文档导航（主入口）
│   ├── ProductSpec             # 产品规格说明
│   ├── guides/                 # 使用指南
│   │   ├── SETUP.md            # 安装配置指南
│   │   ├── QUICKSTART.md       # 快速开始
│   │   ├── FILE_UPLOAD_GUIDE.md    # 文件上传指南
│   │   ├── CONVERSATION_FEATURE.md # 对话功能指南
│   │   ├── EXPORT_FEATURE.md       # 导出功能指南
│   │   └── LOGGING_GUIDE.md        # 日志系统指南
│   ├── architecture/           # 架构文档
│   │   └── PROJECT_STRUCTURE.md    # 项目结构说明
│   └── reports/                # 开发报告
│       ├── BACKEND_COMPLETE.md     # 后端开发总结
│       ├── FRONTEND_COMPLETE.md    # 前端开发总结
│       ├── TERMINAL_TEST_REPORT.md # 终端测试报告
│       └── MCP_TEST_REPORT.md      # MCP 测试报告
│
├── tests/                      # 测试代码
│   └── integration/            # 集成测试
│       ├── test_upload.py
│       ├── test_knowledge.py
│       ├── test_conversation.py
│       ├── test_conversation_context.py
│       └── test_export.py
│
├── scripts/                    # 工具脚本
│   ├── test_all_apis.sh        # 运行所有 API 测试
│   └── view_logs.sh            # 日志查看器
│
├── tools/                      # 开发工具
│   ├── llm_api.py              # LLM API 工具
│   ├── web_scraper.py          # 网页爬虫
│   ├── search_engine.py        # 搜索引擎
│   └── screenshot_utils.py     # 截图工具
│
├── uploads/                    # 上传文件存储
│   └── [project_id]/           # 按项目组织
│       └── [file_id].[ext]     # 文件
│
├── logs/                       # 日志文件
│   ├── app.log                 # 应用日志
│   ├── server.log              # 服务器日志
│   └── server_conversation.log # 对话日志
│
├── venv/                       # Python 虚拟环境
│
├── .cursorrules                # Cursor AI 规则
├── .env                        # 环境变量（不提交）
├── .env.example                # 环境变量示例
├── .gitignore                  # Git 忽略规则
├── requirements.txt            # Python 依赖
├── README.md                   # 项目主文档
├── README_devin.cursorrules.md # Devin 规则
└── PROJECT_ORGANIZATION.md     # 本文件

```

## 📚 文档组织规范

### 文档分类

1. **guides/** - 使用指南
   - 面向用户和开发者的操作指南
   - 包含安装、配置、功能使用等

2. **architecture/** - 架构文档
   - 技术架构说明
   - 项目结构文档
   - 设计决策记录

3. **reports/** - 开发报告
   - 阶段性开发总结
   - 测试报告
   - 性能报告

### 文档命名规范

- 使用大写字母和下划线：`FEATURE_NAME.md`
- 使用描述性名称：`FILE_UPLOAD_GUIDE.md` 而不是 `GUIDE1.md`
- 报告类文档使用 `_REPORT` 或 `_COMPLETE` 后缀

### 文档维护原则

1. **单一入口**：所有文档通过 `docs/README.md` 导航
2. **相对链接**：文档间使用相对路径链接
3. **及时更新**：功能变更时同步更新文档
4. **保持简洁**：避免重复内容，使用链接引用

## 🧪 测试组织规范

### 测试分类

1. **backend/test_api.py** - 后端单元测试
2. **tests/integration/** - 集成测试
   - 按功能模块组织
   - 每个文件测试一个完整功能流程

### 测试命名规范

- 文件名：`test_[feature].py`
- 测试函数：`test_[scenario]_[expected_result]()`

### 运行测试

```bash
# 单个测试
venv/bin/python tests/integration/test_upload.py

# 所有测试
./scripts/test_all_apis.sh
```

## 🛠️ 脚本组织规范

### scripts/ 目录

存放项目相关的工具脚本：
- 测试脚本
- 部署脚本
- 数据库管理脚本
- 日志查看脚本

### tools/ 目录

存放开发工具：
- API 调用工具
- 数据处理工具
- 调试工具

### 脚本命名规范

- 使用小写字母和下划线：`test_all_apis.sh`
- 使用描述性名称
- Shell 脚本使用 `.sh` 扩展名
- Python 脚本使用 `.py` 扩展名

## 📝 日志组织规范

### 日志文件

- `logs/app.log` - 应用主日志
- `logs/server.log` - 服务器日志
- `logs/server_[feature].log` - 功能模块日志

### 日志级别

- **DEBUG**: 详细调试信息
- **INFO**: 一般信息（默认）
- **WARNING**: 警告信息
- **ERROR**: 错误信息

### 日志查看

```bash
# 使用日志查看器
./scripts/view_logs.sh

# 直接查看
tail -f logs/app.log
```

## 📦 上传文件组织

### 目录结构

```
uploads/
└── [project_id]/           # 项目目录
    ├── [file_id].pdf       # 文件以 UUID 命名
    ├── [file_id].png
    └── [file_id].md
```

### 文件管理

- 按项目 ID 组织
- 文件使用 UUID 命名，避免冲突
- 原始文件名存储在数据库中
- 删除项目时清理对应文件

## 🔧 配置文件组织

### 环境变量

- `.env` - 实际配置（不提交到 Git）
- `.env.example` - 配置模板（提交到 Git）

### 配置原则

1. 敏感信息不提交到 Git
2. 提供完整的配置示例
3. 在文档中说明每个配置项的作用

## 📋 新增文件指南

### 添加新文档

1. 确定文档类型（guide/architecture/report）
2. 在对应目录创建文件
3. 更新 `docs/README.md` 添加导航链接
4. 在相关文档中添加交叉引用

### 添加新测试

1. 在 `tests/integration/` 创建测试文件
2. 遵循命名规范：`test_[feature].py`
3. 更新 `scripts/test_all_apis.sh`（如需要）
4. 在文档中说明测试覆盖范围

### 添加新脚本

1. 确定脚本类型（scripts/tools）
2. 在对应目录创建脚本
3. 添加执行权限：`chmod +x script.sh`
4. 在 README 中说明用途

## 🔄 文档更新流程

1. **功能开发完成** → 更新功能文档
2. **测试完成** → 更新测试报告
3. **版本发布** → 更新 CHANGELOG（如有）
4. **架构变更** → 更新架构文档

## 📊 文档质量检查清单

- [ ] 所有文档通过 `docs/README.md` 可访问
- [ ] 文档间链接正确
- [ ] 代码示例可运行
- [ ] 截图清晰（如有）
- [ ] 没有过时信息
- [ ] 没有重复内容

## 🎯 最佳实践

1. **保持整洁**：定期清理过时文件
2. **及时归档**：完成的阶段性文档移到 reports/
3. **统一风格**：遵循项目的文档风格
4. **交叉引用**：相关文档互相链接
5. **版本控制**：重要变更在文档中记录日期

---

最后更新：2025-12-26

如有疑问，请查看 [文档中心](docs/README.md) 或联系项目维护者。

