# AI 模型配置和使用指南 🚀

## 📋 需要配置的 API 密钥

### 1️⃣ Google Gemini（必需，默认使用，免费）
- **获取地址**: https://aistudio.google.com/app/apikey
- **价格**: 免费（有配额限制）
- **特点**: 速度快，支持中文，多模态（文字+图片）

### 2️⃣ OpenAI GPT-4（可选，付费）
- **获取地址**: https://platform.openai.com/api-keys
- **价格**: 输入 $0.01/1K tokens，输出 $0.03/1K tokens
- **特点**: 高质量输出，功能最新

### 3️⃣ Anthropic Claude（可选，付费）
- **获取地址**: https://console.anthropic.com/
- **价格**: 输入 $0.003/1K tokens，输出 $0.015/1K tokens
- **特点**: 推理能力强，超长上下文(200K)

---

## ⚙️ 配置步骤

### 1. 编辑 .env 文件

在项目根目录的 `.env` 文件中添加：

```env
# 1️⃣ Google Gemini（必需）
GEMINI_API_KEY=你的_gemini_密钥

# 2️⃣ OpenAI（可选，如不使用留空）
OPENAI_API_KEY=你的_openai_密钥

# 3️⃣ Claude（可选，如不使用留空）
CLAUDE_API_KEY=你的_claude_密钥
```

### 2. 重启后端服务

```bash
# 如果后端正在运行，需要重启
# 按 Ctrl+C 停止，然后重新启动
source venv/bin/activate
python -m backend.app.main
```

### 3. 刷新前端页面

在浏览器中刷新 http://localhost:5173

---

## 🎯 使用方法

### 在前端切换模型

1. 打开 PRD Sherpa 应用（http://localhost:5173）
2. 在**左侧边栏底部**找到 "AI 模型" 下拉选择器
3. 点击下拉菜单，查看可用的模型
4. 选择想要使用的模型（仅显示已配置的模型）

### 模型标签说明

- 🟢 **免费** - Gemini 模型，免费使用
- 🟠 **付费** - OpenAI 和 Claude，按使用量计费
- 🔴 **未配置** - 需要在 .env 中添加 API 密钥
- 🔵 **当前** - 正在使用的模型

---

## 💡 使用建议

### 日常使用 → Gemini
- ✅ 免费使用
- ✅ 速度快
- ✅ 支持中文
- ✅ 支持图片分析

### 重要 PRD → GPT-4
- ✅ 最高质量
- ✅ 最新功能
- ⚠️ 成本较高

### 技术 PRD → Claude
- ✅ 推理能力强
- ✅ 适合代码相关
- ✅ 超长上下文
- ✅ 性价比高

---

## ⚠️ 注意事项

1. **API 密钥安全**
   - 不要将 `.env` 文件提交到 Git
   - 不要泄露 API 密钥

2. **成本控制**
   - Gemini 有免费配额，超出后收费
   - GPT-4 和 Claude 从第一次调用开始计费
   - 建议只配置实际需要的模型

3. **模型可用性**
   - 未配置 API 密钥的模型会显示"未配置"
   - 无法选择未配置的模型
   - 至少需要配置 Gemini（默认模型）

---

## 🧪 测试配置

### 测试 Gemini
```bash
curl http://localhost:8000/api/ai/providers
# 应该看到 gemini 的 "available": true
```

### 测试模型切换
```bash
# 切换到 GPT-4（如已配置）
curl -X POST http://localhost:8000/api/ai/provider/select \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai"}'
```

---

## 📈 已完成的增强

✅ **多模型支持** - 可在 Gemini、GPT-4、Claude 间切换
✅ **上下文增强** - 对话上下文从 10 条增加到 50 条
✅ **成本追踪** - 实时统计每个模型的使用量和成本
✅ **前端集成** - 侧边栏提供模型选择器

---

## 📞 问题排查

### 问题1: 模型显示"未配置"
**解决**: 在 .env 文件中添加对应的 API 密钥，然后重启后端

### 问题2: 切换模型失败
**解决**: 检查 API 密钥是否正确，查看后端日志

### 问题3: 前端没有显示模型选择器
**解决**: 刷新浏览器页面（Cmd+R 或 F5）

---

## 📚 详细文档

查看完整文档: `docs/AI_MULTI_MODEL_GUIDE.md`

---

**开始使用多模型功能，享受 AI 的灵活性！** ✨
