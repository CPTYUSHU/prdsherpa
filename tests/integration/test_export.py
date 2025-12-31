"""
Test script for PRD export feature.
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def test_export_flow():
    """Test the complete export flow."""
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        print("=" * 60)
        print("测试 PRD 导出功能")
        print("=" * 60)
        print()
        
        # Step 1: Create a project
        print("1️⃣  创建项目...")
        project_data = {
            "name": "电商APP",
            "description": "一个现代化的移动电商应用"
        }
        response = await client.post("/api/projects/", json=project_data)
        assert response.status_code in [200, 201], f"创建项目失败: {response.text}"
        project = response.json()
        project_id = project["id"]
        print(f"✅ 项目创建成功: {project['name']} (ID: {project_id})")
        print()
        
        # Step 2: Upload a test file
        print("2️⃣  上传测试文件...")
        test_content = """
# 电商APP产品需求

## 项目概述
这是一个现代化的移动电商应用，主要面向年轻用户群体。

## 核心功能
1. 用户注册与登录
2. 商品浏览与搜索
3. 购物车管理
4. 订单管理
5. 支付功能
"""
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file_path = f.name
        
        # Upload the file
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_doc.md', f, 'text/markdown')}
            data = {'project_id': project_id}
            response = await client.post("/api/files/upload", files=files, data=data)
        
        import os
        os.unlink(temp_file_path)
        
        assert response.status_code in [200, 201], f"上传文件失败: {response.text}"
        file_data = response.json()
        file_id = file_data["id"]
        print(f"✅ 文件上传成功: {file_data['filename']}")
        print()
        
        # Step 3: Analyze the file
        print("3️⃣  分析文件...")
        response = await client.post(f"/api/files/{file_id}/analyze")
        assert response.status_code == 200, f"分析文件失败: {response.text}"
        print("✅ 文件分析成功")
        print()
        
        # Step 4: Build knowledge base
        print("4️⃣  构建知识库...")
        kb_data = {
            "file_ids": [file_id]
        }
        response = await client.post(f"/api/knowledge/build/{project_id}", json=kb_data)
        assert response.status_code in [200, 201], f"构建知识库失败: {response.text}"
        print("✅ 知识库构建成功")
        print()
        
        # Step 5: Confirm knowledge base
        print("5️⃣  确认知识库...")
        confirm_data = {
            "confirmed_by": "测试用户"
        }
        response = await client.post(f"/api/knowledge/{project_id}/confirm", json=confirm_data)
        assert response.status_code == 200, f"确认知识库失败: {response.text}"
        print("✅ 知识库已确认")
        print()
        
        # Step 6: Create a conversation
        print("6️⃣  创建对话...")
        conv_data = {
            "project_id": project_id,
            "title": "用户登录功能需求"
        }
        response = await client.post("/api/conversations/", json=conv_data)
        assert response.status_code in [200, 201], f"创建对话失败: {response.text}"
        conversation = response.json()
        conversation_id = conversation["id"]
        print(f"✅ 对话创建成功: {conversation['title']} (ID: {conversation_id})")
        print()
        
        # Step 7: Send messages
        print("7️⃣  发送需求消息...")
        messages = [
            "我需要实现一个用户登录功能",
            "支持手机号和邮箱两种方式登录",
            "需要记住密码功能和忘记密码功能"
        ]
        
        for i, msg in enumerate(messages, 1):
            chat_data = {"message": msg}
            response = await client.post(
                f"/api/conversations/{conversation_id}/chat",
                json=chat_data
            )
            assert response.status_code == 200, f"发送消息失败: {response.text}"
            result = response.json()
            print(f"   消息 {i}: {msg}")
            print(f"   AI回复: {result['assistant_message']['content'][:100]}...")
            print()
        
        print("✅ 需求对话完成")
        print()
        
        # Step 8: Export as JSON
        print("8️⃣  导出 PRD (JSON格式)...")
        response = await client.post(
            f"/api/export/conversation/{conversation_id}",
            params={"include_knowledge_base": True}
        )
        assert response.status_code == 200, f"导出失败: {response.text}"
        export_result = response.json()
        print(f"✅ 导出成功")
        print(f"   文件名: {export_result['filename']}")
        print(f"   格式: {export_result['format']}")
        print(f"   内容长度: {len(export_result['content'])} 字符")
        print()
        print("📄 PRD 内容预览:")
        print("-" * 60)
        print(export_result['content'][:500])
        print("...")
        print("-" * 60)
        print()
        
        # Step 9: Download as file
        print("9️⃣  下载 PRD 文件...")
        response = await client.get(
            f"/api/export/conversation/{conversation_id}/download",
            params={"include_knowledge_base": True}
        )
        assert response.status_code == 200, f"下载失败: {response.text}"
        
        # Save to file
        filename = export_result['filename']
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ PRD 文件已保存: {filename}")
        print()
        
        # Step 10: Test export without knowledge base
        print("🔟 测试不包含知识库的导出...")
        response = await client.post(
            f"/api/export/conversation/{conversation_id}",
            params={"include_knowledge_base": False}
        )
        assert response.status_code == 200, f"导出失败: {response.text}"
        export_result2 = response.json()
        print(f"✅ 导出成功 (不含知识库)")
        print(f"   内容长度: {len(export_result2['content'])} 字符")
        print()
        
        # Cleanup
        print("1️⃣1️⃣  清理测试数据...")
        await client.delete(f"/api/conversations/{conversation_id}")
        await client.delete(f"/api/projects/{project_id}")
        print("✅ 测试数据已清理")
        print()
        
        print("=" * 60)
        print("🎉 所有导出功能测试通过！")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_export_flow())

