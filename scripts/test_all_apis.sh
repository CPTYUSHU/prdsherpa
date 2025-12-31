#!/bin/bash

# PRD助手 API 完整测试脚本
# 测试所有 15 个 API 端点

set -e  # 遇到错误立即退出

BASE_URL="http://localhost:8000"
TEST_PASSED=0
TEST_FAILED=0

echo "========================================="
echo "PRD助手 API 完整测试"
echo "========================================="
echo ""

# 创建测试项目
echo "测试 1: POST /api/projects/ - 创建项目"
echo "========================================="
PROJECT_RESULT=$(curl -s -X 'POST' "$BASE_URL/api/projects/" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"name": "API完整测试项目", "description": "用于验证所有API端点"}')

PROJECT_ID=$(echo "$PROJECT_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ 项目创建成功，ID: $PROJECT_ID"
((TEST_PASSED++))
echo ""

# 获取项目列表
echo "测试 2: GET /api/projects/ - 获取项目列表"
echo "========================================="
PROJECTS=$(curl -s -X 'GET' "$BASE_URL/api/projects/" -H 'accept: application/json')
TOTAL=$(echo "$PROJECTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])")
echo "✅ 获取项目列表成功，共 $TOTAL 个项目"
((TEST_PASSED++))
echo ""

# 获取单个项目
echo "测试 3: GET /api/projects/{id} - 获取单个项目"
echo "========================================="
PROJECT=$(curl -s -X 'GET' "$BASE_URL/api/projects/$PROJECT_ID" -H 'accept: application/json')
PROJECT_NAME=$(echo "$PROJECT" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
echo "✅ 获取项目成功，名称: $PROJECT_NAME"
((TEST_PASSED++))
echo ""

# 更新项目
echo "测试 4: PATCH /api/projects/{id} - 更新项目"
echo "========================================="
UPDATED=$(curl -s -X 'PATCH' "$BASE_URL/api/projects/$PROJECT_ID" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"name": "更新后的项目名称", "description": "更新后的描述"}')
NEW_NAME=$(echo "$UPDATED" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
echo "✅ 项目更新成功，新名称: $NEW_NAME"
((TEST_PASSED++))
echo ""

# 创建测试文件
echo "准备测试文件..."
cat > /tmp/api_test_file.txt << EOF
这是一个用于API测试的文档。

系统功能：
- 文件上传
- AI分析
- 知识库管理

技术栈：
- FastAPI
- PostgreSQL
- Gemini AI
EOF

# 上传文件
echo "测试 5: POST /api/files/upload - 上传文件"
echo "========================================="
UPLOAD_RESULT=$(curl -s -X 'POST' "$BASE_URL/api/files/upload" \
  -H 'accept: application/json' \
  -F "file=@/tmp/api_test_file.txt" \
  -F "project_id=$PROJECT_ID")

FILE_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ 文件上传成功，ID: $FILE_ID"
((TEST_PASSED++))
echo ""

# AI 分析文件
echo "测试 6: POST /api/files/{id}/analyze - AI 分析文件"
echo "========================================="
ANALYZE_RESULT=$(curl -s -X 'POST' "$BASE_URL/api/files/$FILE_ID/analyze" \
  -H 'accept: application/json')
ANALYZE_STATUS=$(echo "$ANALYZE_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "✅ AI 分析成功，状态: $ANALYZE_STATUS"
((TEST_PASSED++))
echo ""

# 获取项目文件列表
echo "测试 7: GET /api/files/project/{id} - 获取项目文件列表"
echo "========================================="
FILES=$(curl -s -X 'GET' "$BASE_URL/api/files/project/$PROJECT_ID" -H 'accept: application/json')
FILE_COUNT=$(echo "$FILES" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])")
echo "✅ 获取文件列表成功，共 $FILE_COUNT 个文件"
((TEST_PASSED++))
echo ""

# 构建知识库
echo "测试 8: POST /api/knowledge/build/{id} - 构建知识库"
echo "========================================="
KB_RESULT=$(curl -s -X 'POST' "$BASE_URL/api/knowledge/build/$PROJECT_ID" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{}')
KB_ID=$(echo "$KB_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ 知识库构建成功，ID: $KB_ID"
((TEST_PASSED++))
echo ""

# 获取知识库
echo "测试 9: GET /api/knowledge/{id} - 获取知识库"
echo "========================================="
KB=$(curl -s -X 'GET' "$BASE_URL/api/knowledge/$PROJECT_ID" -H 'accept: application/json')
KB_VERSION=$(echo "$KB" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")
echo "✅ 获取知识库成功，版本: $KB_VERSION"
((TEST_PASSED++))
echo ""

# 更新知识库
echo "测试 10: PATCH /api/knowledge/{id} - 更新知识库"
echo "========================================="
KB_UPDATE=$(curl -s -X 'PATCH' "$BASE_URL/api/knowledge/$PROJECT_ID" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "structured_data": {
      "system_overview": {
        "product_type": "PRD助手系统",
        "core_modules": ["项目管理", "文件管理", "AI分析", "知识库"],
        "description": "一个完整的PRD写作辅助系统"
      },
      "ui_standards": {
        "primary_colors": ["#4299E1", "#48BB78"],
        "component_library": "Ant Design",
        "layout_features": ["响应式布局", "暗色模式"],
        "screenshots": []
      },
      "tech_conventions": {
        "naming_style": "camelCase",
        "api_style": "RESTful",
        "known_fields": [
          {"name": "id", "type": "UUID", "usage": "唯一标识符"},
          {"name": "created_at", "type": "datetime", "usage": "创建时间"}
        ]
      },
      "pending_questions": [],
      "raw_insights": ["系统功能完整", "API设计规范"]
    }
  }')
NEW_VERSION=$(echo "$KB_UPDATE" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")
echo "✅ 知识库更新成功，新版本: $NEW_VERSION"
((TEST_PASSED++))
echo ""

# 确认知识库
echo "测试 11: POST /api/knowledge/{id}/confirm - 确认知识库"
echo "========================================="
KB_CONFIRM=$(curl -s -X 'POST' "$BASE_URL/api/knowledge/$PROJECT_ID/confirm" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"notes": "知识库已确认，可以使用"}')
KB_STATUS=$(echo "$KB_CONFIRM" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "✅ 知识库确认成功，状态: $KB_STATUS"
((TEST_PASSED++))
echo ""

# 删除文件
echo "测试 12: DELETE /api/files/{id} - 删除文件"
echo "========================================="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X 'DELETE' "$BASE_URL/api/files/$FILE_ID" \
  -H 'accept: application/json')
if [ "$HTTP_CODE" = "204" ]; then
  echo "✅ 文件删除成功，HTTP: $HTTP_CODE"
  ((TEST_PASSED++))
else
  echo "❌ 文件删除失败，HTTP: $HTTP_CODE"
  ((TEST_FAILED++))
fi
echo ""

# 删除项目
echo "测试 13: DELETE /api/projects/{id} - 删除项目"
echo "========================================="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X 'DELETE' "$BASE_URL/api/projects/$PROJECT_ID" \
  -H 'accept: application/json')
if [ "$HTTP_CODE" = "204" ]; then
  echo "✅ 项目删除成功，HTTP: $HTTP_CODE"
  ((TEST_PASSED++))
else
  echo "❌ 项目删除失败，HTTP: $HTTP_CODE"
  ((TEST_FAILED++))
fi
echo ""

# 健康检查
echo "测试 14: GET /health - 健康检查"
echo "========================================="
HEALTH=$(curl -s -X 'GET' "$BASE_URL/health" -H 'accept: application/json')
HEALTH_STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "✅ 健康检查通过，状态: $HEALTH_STATUS"
((TEST_PASSED++))
echo ""

# 根路径
echo "测试 15: GET / - 根路径"
echo "========================================="
ROOT=$(curl -s -X 'GET' "$BASE_URL/" -H 'accept: application/json')
ROOT_MSG=$(echo "$ROOT" | python3 -c "import sys, json; print(json.load(sys.stdin)['message'])")
echo "✅ 根路径访问成功，消息: $ROOT_MSG"
((TEST_PASSED++))
echo ""

# 清理测试文件
rm -f /tmp/api_test_file.txt

# 测试总结
echo "========================================="
echo "测试总结"
echo "========================================="
echo "✅ 通过: $TEST_PASSED"
echo "❌ 失败: $TEST_FAILED"
echo "总计: $((TEST_PASSED + TEST_FAILED))"
echo ""

if [ $TEST_FAILED -eq 0 ]; then
  echo "🎉 所有测试通过！"
  exit 0
else
  echo "❌ 有测试失败"
  exit 1
fi

