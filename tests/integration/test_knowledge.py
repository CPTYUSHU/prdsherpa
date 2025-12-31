"""
Test script for knowledge base building.

Usage:
    python test_knowledge.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_knowledge_base_workflow():
    """Test complete knowledge base workflow."""
    
    print("\n" + "="*60)
    print("知识库构建测试")
    print("="*60)
    
    # Step 1: Create project
    print("\n=== Step 1: 创建测试项目 ===")
    project_data = {
        "name": "电商后台系统",
        "description": "一个完整的电商后台管理系统"
    }
    response = requests.post(f"{BASE_URL}/api/projects/", json=project_data)
    print(f"Status: {response.status_code}")
    project = response.json()
    project_id = project["id"]
    print(f"✅ 项目创建成功: {project['name']} (ID: {project_id})")
    
    # Step 2: Upload multiple files
    print("\n=== Step 2: 上传多个测试文件 ===")
    
    # File 1: User management PRD
    file1_content = """
# 用户管理模块 PRD

## 功能概述
用户管理模块负责系统的用户注册、登录、权限管理等功能。

## 数据字段
- userID: string - 用户唯一标识
- userName: string - 用户名
- userEmail: string - 用户邮箱  
- userRole: enum - 用户角色（admin, editor, viewer）
- userStatus: enum - 用户状态（active, inactive, banned）

## API 接口
- POST /api/users/register - 用户注册
- POST /api/users/login - 用户登录
- GET /api/users/{userID} - 获取用户信息
- PUT /api/users/{userID} - 更新用户信息

## UI 规范
- 主色调：#4299E1
- 布局：左侧导航 + 右侧内容区
- 组件库：Ant Design
"""
    
    # File 2: Product management PRD
    file2_content = """
# 商品管理模块 PRD

## 功能概述
商品管理模块负责商品的创建、编辑、上下架等功能。

## 数据字段
- productID: string - 商品唯一标识
- productName: string - 商品名称
- productPrice: number - 商品价格
- productStock: number - 库存数量
- productCategory: string - 商品分类
- productStatus: enum - 商品状态（draft, published, offline）

## API 接口
- POST /api/products - 创建商品
- GET /api/products - 获取商品列表
- GET /api/products/{productID} - 获取商品详情
- PUT /api/products/{productID} - 更新商品
- DELETE /api/products/{productID} - 删除商品

## 技术约定
- 所有ID字段使用camelCase命名
- API采用RESTful风格
- 价格字段使用number类型，单位为分
"""
    
    # File 3: Order management PRD
    file3_content = """
# 订单管理模块 PRD

## 功能概述
订单管理模块负责订单的创建、查询、状态管理等功能。

## 数据字段
- orderID: string - 订单唯一标识
- orderNumber: string - 订单号
- orderStatus: enum - 订单状态（pending, paid, shipped, completed, cancelled）
- orderAmount: number - 订单金额
- orderItems: array - 订单商品列表

## API 接口
- POST /api/orders - 创建订单
- GET /api/orders - 获取订单列表
- GET /api/orders/{orderID} - 获取订单详情
- PATCH /api/orders/{orderID}/status - 更新订单状态

## UI 规范
- 订单列表使用表格展示
- 订单状态使用不同颜色的标签
- 支持订单搜索和筛选
"""
    
    files_to_upload = [
        ("user_management.md", file1_content),
        ("product_management.md", file2_content),
        ("order_management.md", file3_content),
    ]
    
    uploaded_files = []
    for filename, content in files_to_upload:
        # Save to temp file
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Upload
        with open(temp_path, 'rb') as f:
            files = {'file': (filename, f, 'text/markdown')}
            data = {'project_id': project_id}
            response = requests.post(f"{BASE_URL}/api/files/upload", files=files, data=data)
        
        if response.status_code == 201:
            file_data = response.json()
            uploaded_files.append(file_data)
            print(f"✅ 上传成功: {filename}")
        else:
            print(f"❌ 上传失败: {filename} - {response.text}")
    
    # Step 3: Analyze all files
    print("\n=== Step 3: AI 分析所有文件 ===")
    for file_data in uploaded_files:
        file_id = file_data['id']
        filename = file_data['filename']
        print(f"分析中: {filename}...")
        
        response = requests.post(f"{BASE_URL}/api/files/{file_id}/analyze")
        if response.status_code == 200:
            print(f"  ✅ 分析完成")
        else:
            print(f"  ❌ 分析失败: {response.text}")
        
        time.sleep(1)  # Avoid rate limiting
    
    # Step 4: Build knowledge base
    print("\n=== Step 4: 构建项目知识库 ===")
    response = requests.post(
        f"{BASE_URL}/api/knowledge/build/{project_id}",
        json={"force_rebuild": False}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        kb = response.json()
        print(f"\n✅ 知识库构建成功!")
        print(f"版本: {kb['version']}")
        print(f"状态: {kb['status']}")
        
        # Display knowledge base content
        kb_data = kb['structured_data']
        
        print("\n" + "="*60)
        print("📦 系统概览")
        print("="*60)
        overview = kb_data.get('system_overview', {})
        print(f"产品类型: {overview.get('product_type', '未知')}")
        print(f"核心模块: {', '.join(overview.get('core_modules', []))}")
        if overview.get('description'):
            print(f"描述: {overview['description']}")
        
        print("\n" + "="*60)
        print("🎨 UI 规范")
        print("="*60)
        ui = kb_data.get('ui_standards', {})
        if ui.get('primary_colors'):
            print(f"主色调: {', '.join(ui['primary_colors'])}")
        if ui.get('component_library'):
            print(f"组件库: {ui['component_library']}")
        if ui.get('layout_features'):
            print(f"布局特征: {', '.join(ui['layout_features'])}")
        
        print("\n" + "="*60)
        print("🔧 技术约定")
        print("="*60)
        tech = kb_data.get('tech_conventions', {})
        if tech.get('naming_style'):
            print(f"命名风格: {tech['naming_style']}")
        if tech.get('api_style'):
            print(f"API 风格: {tech['api_style']}")
        if tech.get('known_fields'):
            print(f"\n已识别字段 ({len(tech['known_fields'])} 个):")
            for field in tech['known_fields'][:5]:  # Show first 5
                print(f"  - {field.get('name')}: {field.get('type')} - {field.get('usage', '')}")
            if len(tech['known_fields']) > 5:
                print(f"  ... 还有 {len(tech['known_fields']) - 5} 个字段")
        
        print("\n" + "="*60)
        print("❓ 待确认问题")
        print("="*60)
        questions = kb_data.get('pending_questions', [])
        if questions:
            for i, q in enumerate(questions, 1):
                print(f"\n{i}. {q.get('question')}")
                if q.get('context'):
                    print(f"   背景: {q['context']}")
                if q.get('suggested_answer'):
                    print(f"   建议: {q['suggested_answer']}")
        else:
            print("无待确认问题")
        
        # Step 5: Get knowledge base
        print("\n=== Step 5: 查看知识库 ===")
        response = requests.get(f"{BASE_URL}/api/knowledge/{project_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ 知识库获取成功")
        
        # Step 6: Confirm knowledge base
        print("\n=== Step 6: 确认知识库 ===")
        response = requests.post(
            f"{BASE_URL}/api/knowledge/{project_id}/confirm",
            json={
                "answers": {
                    "订单支付方式": "支持微信、支付宝、银行卡支付"
                },
                "notes": "知识库已确认，可以开始写需求"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            kb = response.json()
            print(f"✅ 知识库已确认 (版本: {kb['version']}, 状态: {kb['status']})")
        
        print("\n" + "="*60)
        print("✅ 所有测试完成!")
        print("="*60)
        print(f"\n项目ID: {project_id}")
        print(f"可以在 Swagger UI 中查看: http://localhost:8000/docs")
        print(f"清理测试数据: curl -X DELETE {BASE_URL}/api/projects/{project_id}")
    
    else:
        print(f"❌ 知识库构建失败: {response.text}")


if __name__ == "__main__":
    try:
        test_knowledge_base_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

