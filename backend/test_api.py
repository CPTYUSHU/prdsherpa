"""
Simple API test script.
Tests the project management endpoints.

Usage:
    # Make sure the server is running on http://localhost:8000
    python backend/test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200


def test_create_project():
    """Test creating a project."""
    print("\n=== Testing Create Project ===")
    data = {
        "name": "测试CMS系统",
        "description": "这是一个测试项目，用于验证API功能"
    }
    response = requests.post(f"{BASE_URL}/api/projects/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 201
    return response.json()["id"]


def test_list_projects():
    """Test listing projects."""
    print("\n=== Testing List Projects ===")
    response = requests.get(f"{BASE_URL}/api/projects/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total projects: {data['total']}")
    print(f"Projects: {json.dumps(data['projects'], indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_get_project(project_id):
    """Test getting a specific project."""
    print(f"\n=== Testing Get Project {project_id} ===")
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_update_project(project_id):
    """Test updating a project."""
    print(f"\n=== Testing Update Project {project_id} ===")
    data = {
        "name": "更新后的CMS系统",
        "description": "描述已更新"
    }
    response = requests.patch(f"{BASE_URL}/api/projects/{project_id}", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_delete_project(project_id):
    """Test deleting a project."""
    print(f"\n=== Testing Delete Project {project_id} ===")
    response = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
    print(f"Status: {response.status_code}")
    assert response.status_code == 204


def main():
    """Run all tests."""
    try:
        # Test health check
        test_health_check()
        
        # Test project CRUD
        project_id = test_create_project()
        test_list_projects()
        test_get_project(project_id)
        test_update_project(project_id)
        test_list_projects()
        test_delete_project(project_id)
        
        print("\n✅ All tests passed!")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server. Make sure it's running on http://localhost:8000")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()

