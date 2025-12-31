# Git 仓库推送指南

> 快速指南：如何将项目推送到远程 Git 仓库（GitHub/GitLab/Gitee）

## 前提检查

### ✅ 已完成的安全配置

1. **敏感文件已被忽略**
   - `.env` 文件 ✓ （包含 API 密钥）
   - `*.db` 数据库文件 ✓
   - `logs/*.log` 日志文件 ✓
   - `uploads/` 上传文件 ✓
   - `venv/` 虚拟环境 ✓

2. **配置模板已就绪**
   - `.env.example` ✓ （安全的配置模板）
   - `DEPLOYMENT_GUIDE.md` ✓ （完整使用说明）

## 推送到远程仓库

### 方式 1: GitHub

#### 1. 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 填写仓库名称: `prdsherpa`
3. 选择"Private"（私有）或"Public"（公开）
4. 不要初始化 README（我们已有）
5. 点击"Create repository"

#### 2. 推送代码

```bash
# 配置用户信息（如果未配置）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"

# 将文件添加到暂存区
git add .

# 提交代码
git commit -m "feat: 初始化 PRD Sherpa 项目

- 完整的前后端代码
- 支持多 AI 模型切换（Gemini/GPT-4/Claude）
- 包含部署文档和使用指南
"

# 添加远程仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/prdsherpa.git

# 推送代码
git branch -M main  # 重命名分支为 main
git push -u origin main
```

#### 3. 验证推送成功

访问你的 GitHub 仓库，应该能看到所有文件。

**重要检查**:
- [ ] .env 文件不在仓库中 ✓
- [ ] .env.example 文件存在 ✓
- [ ] DEPLOYMENT_GUIDE.md 文件存在 ✓

---

### 方式 2: GitLab

```bash
# 1. 在 GitLab 创建新项目
# 访问: https://gitlab.com/projects/new

# 2. 推送代码
git remote add origin https://gitlab.com/你的用户名/prdsherpa.git
git branch -M main
git push -u origin main
```

---

### 方式 3: Gitee（码云）

```bash
# 1. 在 Gitee 创建新仓库
# 访问: https://gitee.com/projects/new

# 2. 推送代码
git remote add origin https://gitee.com/你的用户名/prdsherpa.git
git branch -M master  # Gitee 默认使用 master
git push -u origin master
```

---

## 团队成员克隆仓库

### 1. 克隆代码

```bash
# GitHub
git clone https://github.com/你的用户名/prdsherpa.git

# GitLab
git clone https://gitlab.com/你的用户名/prdsherpa.git

# Gitee
git clone https://gitee.com/你的用户名/prdsherpa.git

cd prdsherpa
```

### 2. 配置环境

```bash
# 1. 复制环境配置模板
cp .env.example .env

# 2. 编辑 .env 文件，填入自己的 API Key
nano .env  # 或使用其他编辑器

# 3. 按照 DEPLOYMENT_GUIDE.md 完成后续配置
```

### 3. 启动服务

```bash
# 按照 DEPLOYMENT_GUIDE.md 中的步骤操作
# 1. 安装后端依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 安装前端依赖
cd frontend
npm install
cd ..

# 3. 初始化数据库
python backend/init_db.py

# 4. 启动服务
# 终端 1
source venv/bin/activate
python -m backend.app.main

# 终端 2
cd frontend
npm run dev
```

---

## 日常开发工作流

### 拉取最新代码

```bash
git pull origin main
```

### 提交代码

```bash
# 1. 查看修改
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "描述你的修改"

# 4. 推送
git push origin main
```

### 创建功能分支

```bash
# 创建并切换到新分支
git checkout -b feature/新功能名称

# 开发完成后推送
git push -u origin feature/新功能名称

# 在 GitHub/GitLab 创建 Pull Request/Merge Request
```

---

## 常见问题

### 1. 推送时提示认证失败

**GitHub 解决方案**（推荐使用 Personal Access Token）:

```bash
# 1. 生成 Token
# 访问: https://github.com/settings/tokens
# 点击 "Generate new token (classic)"
# 勾选 "repo" 权限
# 复制生成的 token

# 2. 使用 Token 推送
git remote set-url origin https://你的token@github.com/你的用户名/prdsherpa.git
git push -u origin main
```

### 2. 误提交了 .env 文件怎么办？

```bash
# 立即从仓库中删除（保留本地文件）
git rm --cached .env
git commit -m "chore: 移除误提交的 .env 文件"
git push origin main

# 如果已经推送，需要更换 API Key！
```

### 3. 查看哪些文件会被提交

```bash
# 查看所有被忽略的文件
git status --ignored

# 测试文件是否会被忽略
git add -n 文件名
```

### 4. 更新 .gitignore 后清理已跟踪的文件

```bash
# 清除 Git 缓存
git rm -r --cached .
git add .
git commit -m "chore: 更新 .gitignore 规则"
```

---

## 安全提示

### 🔒 绝对不要提交的文件

- [ ] `.env` - 包含 API 密钥
- [ ] `*.db` - 数据库文件
- [ ] `logs/*.log` - 日志文件
- [ ] `uploads/*` - 用户上传文件
- [ ] `venv/` - Python 虚拟环境
- [ ] `node_modules/` - 前端依赖

### ✅ 应该提交的文件

- [x] `.env.example` - 配置模板
- [x] `requirements.txt` - Python 依赖列表
- [x] `frontend/package.json` - 前端依赖列表
- [x] `DEPLOYMENT_GUIDE.md` - 部署文档
- [x] 所有源代码文件

### 🚨 紧急情况处理

如果不小心泄露了 API Key：

1. **立即更换 API Key**
   - Gemini: https://aistudio.google.com/app/apikey
   - OpenAI: https://platform.openai.com/api-keys
   - Claude: https://console.anthropic.com/

2. **从 Git 历史中删除敏感信息**
   ```bash
   # 使用 BFG Repo-Cleaner 或 git-filter-repo
   # 注意：这会重写 Git 历史，需谨慎操作
   ```

3. **通知团队成员拉取最新代码**

---

## 项目仓库设置建议

### 1. 添加仓库描述

```
PRD Sherpa - AI-powered Product Requirements Document (PRD) writing assistant
基于 AI 的产品需求文档写作助手，支持 Gemini/GPT-4/Claude 多模型
```

### 2. 添加标签

```
prd, ai, gemini, gpt-4, claude, fastapi, react, typescript
```

### 3. 设置仓库权限

- **公开仓库**: 注意不要在 Issue/PR 中泄露 API Key
- **私有仓库**: 邀请团队成员时确认身份

### 4. 启用分支保护

GitHub Settings → Branches → Add rule:
- Branch name pattern: `main`
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging

---

## 团队协作建议

### 1. Code Review 流程

1. 创建功能分支
2. 开发并测试
3. 提交 Pull Request
4. 至少一人 Review
5. 合并到 main

### 2. Commit Message 规范

```bash
# 格式: <type>: <subject>

# 类型:
feat:     新功能
fix:      修复 Bug
docs:     文档更新
style:    代码格式调整
refactor: 重构
test:     测试相关
chore:    构建/工具相关

# 示例:
git commit -m "feat: 添加 GPT-4 模型支持"
git commit -m "fix: 修复文件上传失败问题"
git commit -m "docs: 更新部署文档"
```

### 3. 分支命名规范

```bash
feature/功能名称   # 新功能
bugfix/问题描述    # Bug 修复
hotfix/紧急修复    # 紧急修复
docs/文档更新      # 文档更新
```

---

## 资源链接

- **项目文档**: `DEPLOYMENT_GUIDE.md`
- **快速参考**: `QUICK_REFERENCE.md`
- **API 文档**: http://localhost:8000/docs
- **GitHub 文档**: https://docs.github.com/
- **Git 教程**: https://git-scm.com/book/zh/v2

---

祝推送顺利！记得保护好你的 API Key 🔐
