"""
Test script for file upload and analysis API.

Usage:
    python test_upload.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_file_upload_and_analysis():
    """Test file upload and AI analysis workflow."""
    
    print("\n=== Step 1: Create a test project ===")
    project_data = {
        "name": "测试文件上传项目",
        "description": "用于测试文件上传和AI分析功能"
    }
    response = requests.post(f"{BASE_URL}/api/projects/", json=project_data)
    print(f"Status: {response.status_code}")
    project = response.json()
    project_id = project["id"]
    print(f"Project created: {project['name']} (ID: {project_id})")
    
    print("\n=== Step 2: Create a test document ===")
    test_content = """
# 用户管理模块 PRD

## 功能概述
用户管理模块负责系统的用户注册、登录、权限管理等功能。

## 数据字段
- userID: string - 用户唯一标识
- userName: string - 用户名
- userEmail: string - 用户邮箱
- userRole: enum - 用户角色（admin, editor, viewer）

## API 接口
- POST /api/users/register - 用户注册
- POST /api/users/login - 用户登录
- GET /api/users/{userID} - 获取用户信息

## UI 规范
- 主色调：#4299E1
- 布局：左侧导航 + 右侧内容区
- 组件库：Ant Design
"""
    
    # Save to file
    test_file_path = "/tmp/test_prd.md"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"Test file created: {test_file_path}")
    
    print("\n=== Step 3: Upload file ===")
    with open(test_file_path, 'rb') as f:
        files = {'file': ('test_prd.md', f, 'text/markdown')}
        data = {'project_id': project_id}
        response = requests.post(f"{BASE_URL}/api/files/upload", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        uploaded_file = response.json()
        file_id = uploaded_file["id"]
        print(f"File uploaded successfully!")
        print(f"  - File ID: {file_id}")
        print(f"  - Filename: {uploaded_file['filename']}")
        print(f"  - Size: {uploaded_file['file_size']} bytes")
        print(f"  - Status: {uploaded_file['status']}")
        
        print("\n=== Step 4: Analyze file with AI ===")
        response = requests.post(f"{BASE_URL}/api/files/{file_id}/analyze")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"\n✅ Analysis completed!")
            print(f"\nAnalysis result:")
            print(json.dumps(analysis['analysis'], indent=2, ensure_ascii=False))
        else:
            print(f"❌ Analysis failed: {response.text}")
        
        print("\n=== Step 5: List project files ===")
        response = requests.get(f"{BASE_URL}/api/files/project/{project_id}")
        print(f"Status: {response.status_code}")
        files_list = response.json()
        print(f"Total files: {files_list['total']}")
        for file in files_list['files']:
            print(f"  - {file['filename']} ({file['status']})")
            if file['analysis_result']:
                print(f"    Summary: {file['analysis_result'][:100]}...")
        
        print("\n=== Step 6: Cleanup (optional) ===")
        print("To delete the test project and files:")
        print(f"  curl -X DELETE {BASE_URL}/api/projects/{project_id}")
    
    else:
        print(f"❌ Upload failed: {response.text}")


if __name__ == "__main__":
    try:
        test_file_upload_and_analysis()
        print("\n✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

