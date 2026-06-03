import sys
import os
from itertools import count
import pytest

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, store


@pytest.fixture
def client():
    store._tasks.clear()
    store._ids = count(1)
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


def test_get_task_by_id_success(client):
    created = client.post("/tasks", json={"title": "A"}).get_json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.get_json() == created


def test_get_task_by_id_not_found(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "task not found"}


def test_update_task_title_only(client):
    created = client.post(
        "/tasks", json={"title": "Initial", "status": "pending"}
    ).get_json()

    response = client.put(f"/tasks/{created['id']}", json={"title": "Updated"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "Updated"
    assert body["status"] == "pending"


def test_update_task_status_only(client):
    created = client.post(
        "/tasks", json={"title": "Initial", "status": "pending"}
    ).get_json()

    response = client.put(f"/tasks/{created['id']}", json={"status": "done"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "Initial"
    assert body["status"] == "done"


def test_update_task_title_and_status(client):
    created = client.post(
        "/tasks", json={"title": "Initial", "status": "pending"}
    ).get_json()

    response = client.put(
        f"/tasks/{created['id']}", json={"title": "Updated", "status": "in_progress"}
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "Updated"
    assert body["status"] == "in_progress"


def test_update_task_not_found(client):
    response = client.put("/tasks/999", json={"title": "Nope"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "task not found"}


@pytest.mark.parametrize(
    "payload,error_message",
    [
        ({"title": ""}, "title must be a non-empty string"),
        ({"title": 123}, "title must be a non-empty string"),
    ],
)
def test_update_task_invalid_title_returns_400(client, payload, error_message):
    created = client.post("/tasks", json={"title": "Initial"}).get_json()

    response = client.put(f"/tasks/{created['id']}", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": error_message}


def test_update_task_invalid_status_returns_422(client):
    created = client.post("/tasks", json={"title": "Initial"}).get_json()

    response = client.put(f"/tasks/{created['id']}", json={"status": "blocked"})

    assert response.status_code == 422
    assert response.get_json() == {
        "error": "status must be one of: pending, in_progress, done",
        "valid_statuses": ["done", "in_progress", "pending"],
    }


def test_delete_task_success_returns_204(client):
    created = client.post("/tasks", json={"title": "Delete me"}).get_json()

    response = client.delete(f"/tasks/{created['id']}")
    get_deleted = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert response.data == b""
    assert get_deleted.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "task not found"}


def test_list_tasks_filter_by_known_status(client):
    client.post("/tasks", json={"title": "A", "status": "pending"})
    client.post("/tasks", json={"title": "B", "status": "done"})
    client.post("/tasks", json={"title": "C", "status": "done"})

    response = client.get("/tasks?status=done")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    assert all(task["status"] == "done" for task in body)


def test_list_tasks_filter_unknown_status_returns_empty_list(client):
    client.post("/tasks", json={"title": "A", "status": "pending"})

    response = client.get("/tasks?status=unknown")

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_tasks_without_filter_returns_all(client):
    client.post("/tasks", json={"title": "A", "status": "pending"})
    client.post("/tasks", json={"title": "B", "status": "in_progress"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_create_task_missing_title_returns_400(client):
    response = client.post("/tasks", json={"status": "pending"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "title is required"}


@pytest.mark.parametrize(
    "payload,error_message",
    [
        ({"title": ""}, "title must be a non-empty string"),
        ({"title": "   "}, "title must be a non-empty string"),
        ({"title": 123}, "title must be a non-empty string"),
    ],
)
def test_create_task_invalid_title_returns_400(client, payload, error_message):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": error_message}


def test_create_task_invalid_status_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "status": "blocked"})

    assert response.status_code == 422
    assert response.get_json() == {
        "error": "status must be one of: pending, in_progress, done",
        "valid_statuses": ["done", "in_progress", "pending"],
    }
