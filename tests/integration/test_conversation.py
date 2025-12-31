#!/usr/bin/env python3
"""
Test script for conversation API.
"""
import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import httpx


BASE_URL = "http://localhost:8000"


async def test_conversation_flow():
    """Test complete conversation flow."""
    # Increase timeout for AI operations
    timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        print("=" * 60)
        print("对话功能测试")
        print("=" * 60)
        print()
        
        # Step 1: Create a project
        print("步骤 1: 创建测试项目")
        print("-" * 60)
        project_data = {
            "name": "对话测试项目",
            "description": "用于测试对话功能的项目"
        }
        response = await client.post(f"{BASE_URL}/api/projects/", json=project_data)
        assert response.status_code == 201, f"创建项目失败: {response.text}"
        project = response.json()
        project_id = project["id"]
        print(f"✅ 项目创建成功")
        print(f"   项目ID: {project_id}")
        print(f"   项目名称: {project['name']}")
        print()
        
        # Step 2: Upload a test file
        print("步骤 2: 上传测试文件")
        print("-" * 60)
        test_content = """这是一个电商系统的需求文档。

系统功能：
- 用户管理：注册、登录、个人信息管理
- 商品管理：商品列表、商品详情、商品搜索
- 订单管理：创建订单、支付订单、查看订单历史
- 购物车：添加商品、修改数量、删除商品

UI规范：
- 主色调：蓝色 (#1890ff)
- 组件库：Ant Design
- 布局：响应式布局

技术约定：
- API风格：RESTful
- 命名规范：camelCase
- 字段：userId (用户ID), productId (商品ID), orderId (订单ID)
"""
        
        files = {"file": ("test_doc.txt", test_content, "text/plain")}
        data = {"project_id": project_id}
        response = await client.post(f"{BASE_URL}/api/files/upload", files=files, data=data)
        assert response.status_code == 201, f"上传文件失败: {response.text}"
        file_info = response.json()
        file_id = file_info["id"]
        print(f"✅ 文件上传成功")
        print(f"   文件ID: {file_id}")
        print()
        
        # Step 3: Analyze file
        print("步骤 3: AI 分析文件")
        print("-" * 60)
        response = await client.post(f"{BASE_URL}/api/files/{file_id}/analyze")
        assert response.status_code == 200, f"分析文件失败: {response.text}"
        analysis = response.json()
        print(f"✅ 文件分析完成")
        print(f"   摘要: {analysis['analysis']['summary'][:50]}...")
        print()
        
        # Step 4: Build knowledge base
        print("步骤 4: 构建知识库")
        print("-" * 60)
        response = await client.post(f"{BASE_URL}/api/knowledge/build/{project_id}", json={})
        assert response.status_code in [200, 201], f"构建知识库失败 (HTTP {response.status_code}): {response.text}"
        kb = response.json()
        print(f"✅ 知识库构建成功")
        print(f"   知识库ID: {kb['id']}")
        print(f"   产品类型: {kb['structured_data']['system_overview'].get('product_type', 'N/A')}")
        print()
        
        # Step 5: Confirm knowledge base
        print("步骤 5: 确认知识库")
        print("-" * 60)
        response = await client.post(
            f"{BASE_URL}/api/knowledge/{project_id}/confirm",
            json={"notes": "知识库确认完成"}
        )
        assert response.status_code == 200, f"确认知识库失败: {response.text}"
        print(f"✅ 知识库已确认")
        print()
        
        # Step 6: Create conversation
        print("步骤 6: 创建对话")
        print("-" * 60)
        conv_data = {"project_id": project_id}
        response = await client.post(f"{BASE_URL}/api/conversations/", json=conv_data)
        assert response.status_code == 201, f"创建对话失败: {response.text}"
        conversation = response.json()
        conversation_id = conversation["id"]
        print(f"✅ 对话创建成功")
        print(f"   对话ID: {conversation_id}")
        print()
        
        # Step 7: First chat message
        print("步骤 7: 发送第一条消息")
        print("-" * 60)
        user_message_1 = "我想增加一个会员积分功能，用户购买商品可以获得积分，积分可以用来兑换优惠券。"
        print(f"👤 用户: {user_message_1}")
        print()
        
        chat_data = {"message": user_message_1}
        response = await client.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/chat",
            json=chat_data
        )
        assert response.status_code == 200, f"发送消息失败: {response.text}"
        chat_response = response.json()
        
        print(f"🤖 AI: {chat_response['assistant_message']['content'][:200]}...")
        print()
        
        # Step 8: Second chat message
        print("步骤 8: 发送第二条消息")
        print("-" * 60)
        user_message_2 = "积分规则是每消费1元获得1积分，100积分可以兑换10元优惠券。"
        print(f"👤 用户: {user_message_2}")
        print()
        
        chat_data = {"message": user_message_2}
        response = await client.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/chat",
            json=chat_data
        )
        assert response.status_code == 200, f"发送消息失败: {response.text}"
        chat_response = response.json()
        
        print(f"🤖 AI: {chat_response['assistant_message']['content'][:200]}...")
        print()
        
        # Step 9: Get conversation with all messages
        print("步骤 9: 获取完整对话历史")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/api/conversations/{conversation_id}")
        assert response.status_code == 200, f"获取对话失败: {response.text}"
        full_conversation = response.json()
        
        print(f"✅ 对话标题: {full_conversation.get('title', '无标题')}")
        print(f"   消息数量: {len(full_conversation['messages'])}")
        print(f"   创建时间: {full_conversation['created_at']}")
        print()
        
        print("对话历史:")
        for i, msg in enumerate(full_conversation['messages'], 1):
            role_emoji = "👤" if msg['role'] == "user" else "🤖"
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"  {i}. {role_emoji} {msg['role']}: {content_preview}")
        print()
        
        # Step 10: List project conversations
        print("步骤 10: 获取项目的所有对话")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/api/conversations/project/{project_id}")
        assert response.status_code == 200, f"获取对话列表失败: {response.text}"
        conversations = response.json()
        
        print(f"✅ 项目共有 {conversations['total']} 个对话")
        for conv in conversations['conversations']:
            print(f"   - {conv.get('title', '无标题')} ({conv['message_count']} 条消息)")
        print()
        
        # Step 11: Clean up - Delete conversation
        print("步骤 11: 删除对话")
        print("-" * 60)
        response = await client.delete(f"{BASE_URL}/api/conversations/{conversation_id}")
        assert response.status_code == 204, f"删除对话失败: {response.status_code}"
        print(f"✅ 对话已删除")
        print()
        
        # Step 12: Clean up - Delete project
        print("步骤 12: 删除项目")
        print("-" * 60)
        response = await client.delete(f"{BASE_URL}/api/projects/{project_id}")
        assert response.status_code == 204, f"删除项目失败: {response.status_code}"
        print(f"✅ 项目已删除")
        print()
        
        print("=" * 60)
        print("🎉 所有对话功能测试通过！")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_conversation_flow())
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

