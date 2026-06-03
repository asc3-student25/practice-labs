import sys
import os
import pytest

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, store


@pytest.fixture
def client():
    store._tasks.clear()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task_returns_201_with_task(client):
    response = client.post("/tasks", json={"title": "Write docs"})
    assert response.status_code == 201
    body = response.get_json()
    assert body["title"] == "Write docs"
    assert body["status"] == "pending"
    assert "id" in body


def test_create_task_missing_title_returns_400(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_task_invalid_status_returns_400(client):
    response = client.post("/tasks", json={"title": "Go", "status": "urgent"})
    assert response.status_code == 400


def test_get_task_returns_task(client):
    created = client.post("/tasks", json={"title": "Read"}).get_json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Read"


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task_changes_fields(client):
    created = client.post("/tasks", json={"title": "Draft"}).get_json()
    response = client.put(
        f"/tasks/{created['id']}",
        json={"status": "in_progress"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "Draft"
    assert body["status"] == "in_progress"


def test_update_task_not_found(client):
    response = client.put("/tasks/999", json={"status": "done"})
    assert response.status_code == 404


def test_update_task_invalid_status(client):
    created = client.post("/tasks", json={"title": "X"}).get_json()
    response = client.put(f"/tasks/{created['id']}", json={"status": "nope"})
    assert response.status_code == 400


def test_delete_task_returns_204(client):
    created = client.post("/tasks", json={"title": "Temp"}).get_json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_list_filters_by_status(client):
    client.post("/tasks", json={"title": "A", "status": "pending"})
    client.post("/tasks", json={"title": "B", "status": "done"})
    client.post("/tasks", json={"title": "C", "status": "done"})

    response = client.get("/tasks?status=done")
    assert response.status_code == 200
    titles = [t["title"] for t in response.get_json()]
    assert sorted(titles) == ["B", "C"]


def test_list_unknown_status_returns_empty(client):
    client.post("/tasks", json={"title": "A"})
    response = client.get("/tasks?status=unknown")
    assert response.status_code == 200
    assert response.get_json() == []
