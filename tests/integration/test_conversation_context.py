#!/usr/bin/env python3
"""
Test conversation context and history.
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_context():
    timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Create project
        resp = await client.post(f"{BASE_URL}/api/projects/", json={
            "name": "上下文测试", "description": "测试对话上下文"
        })
        project_id = resp.json()["id"]
        print(f"✅ 项目ID: {project_id}")
        
        # Create conversation
        resp = await client.post(f"{BASE_URL}/api/conversations/", json={
            "project_id": project_id
        })
        conv_id = resp.json()["id"]
        print(f"✅ 对话ID: {conv_id}")
        
        # First message
        print("\n👤 第一条消息: 我的名字是小明")
        resp = await client.post(f"{BASE_URL}/api/conversations/{conv_id}/chat", json={
            "message": "我的名字是小明"
        })
        ai_msg = resp.json()["assistant_message"]["content"]
        print(f"🤖 AI回复: {ai_msg[:100]}...")
        
        # Second message - test if AI remembers
        print("\n👤 第二条消息: 你还记得我的名字吗？")
        resp = await client.post(f"{BASE_URL}/api/conversations/{conv_id}/chat", json={
            "message": "你还记得我的名字吗？"
        })
        ai_msg = resp.json()["assistant_message"]["content"]
        print(f"🤖 AI回复: {ai_msg}")
        
        # Check if AI mentions "小明"
        if "小明" in ai_msg:
            print("\n✅ AI 记住了名字！对话上下文工作正常！")
        else:
            print("\n❌ AI 没有记住名字，对话上下文可能有问题")
        
        # Clean up
        await client.delete(f"{BASE_URL}/api/projects/{project_id}")

asyncio.run(test_context())
