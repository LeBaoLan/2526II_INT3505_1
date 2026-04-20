import pytest
import requests

BASE = "http://127.0.0.1:3000"


@pytest.fixture(scope="session", autouse=True)
def warmup():
    """Gửi request đầu tiên để Flask khởi động xong trước khi test"""
    requests.get(f"{BASE}/todos")


def test_get_todos():
    r = requests.get(f"{BASE}/todos")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert r.elapsed.total_seconds() < 0.5  # giờ sẽ pass


def test_create_todo():
    r = requests.post(f"{BASE}/todos", json={"title": "Test item"})
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["title"] == "Test item"
    assert data["done"] == False


def test_get_todo_by_id():
    # Tạo trước rồi lấy
    created = requests.post(f"{BASE}/todos", json={"title": "Find me"}).json()
    r = requests.get(f"{BASE}/todos/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_update_todo():
    created = requests.post(
        f"{BASE}/todos", json={"title": "Old title"}).json()
    r = requests.put(f"{BASE}/todos/{created['id']}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] == True


def test_delete_todo():
    created = requests.post(
        f"{BASE}/todos", json={"title": "Delete me"}).json()
    r = requests.delete(f"{BASE}/todos/{created['id']}")
    assert r.status_code == 204
    # Kiểm tra đã xóa thật
    r2 = requests.get(f"{BASE}/todos/{created['id']}")
    assert r2.status_code == 404


def test_get_nonexistent():
    r = requests.get(f"{BASE}/todos/99999")
    assert r.status_code == 404
