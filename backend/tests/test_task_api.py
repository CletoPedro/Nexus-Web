"""
Task API tests, run against the real Postgres database — no mocking of
the repository or database layer.
"""




def test_create_and_get_task(client):
    resp = client.post("/api/v1/tasks", json={"title": "Buy milk"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Buy milk"
    assert body["status"] == "TODO"
    assert body["priority"] == "MEDIUM"

    task_id = body["id"]
    resp = client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id

    client.delete(f"/api/v1/tasks/{task_id}")


def test_create_rejects_empty_title(client):
    resp = client.post("/api/v1/tasks", json={"title": "   "})
    assert resp.status_code == 422


def test_create_with_priority_and_due_date(client):
    resp = client.post(
        "/api/v1/tasks",
        json={
            "title": "File taxes",
            "priority": "HIGH",
            "due_date": "2026-12-31T23:59:59Z",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["priority"] == "HIGH"
    assert body["due_date"] is not None

    client.delete(f"/api/v1/tasks/{body['id']}")


def test_create_rejects_invalid_priority(client):
    resp = client.post("/api/v1/tasks", json={"title": "Bad task", "priority": "URGENT"})
    assert resp.status_code == 422


def test_list_tasks_includes_created(client):
    resp = client.post("/api/v1/tasks", json={"title": "List-test task"})
    task_id = resp.json()["id"]

    resp = client.get("/api/v1/tasks")
    assert resp.status_code == 200
    ids = [t["id"] for t in resp.json()]
    assert task_id in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_list_filters_by_status(client):
    todo_resp = client.post("/api/v1/tasks", json={"title": "Stays todo"})
    todo_id = todo_resp.json()["id"]
    done_resp = client.post("/api/v1/tasks", json={"title": "Will be done"})
    done_id = done_resp.json()["id"]
    client.put(f"/api/v1/tasks/{done_id}/status", json={"status": "DONE"})

    resp = client.get("/api/v1/tasks", params={"status": "DONE"})
    ids = [t["id"] for t in resp.json()]
    assert done_id in ids
    assert todo_id not in ids

    client.delete(f"/api/v1/tasks/{todo_id}")
    client.delete(f"/api/v1/tasks/{done_id}")


def test_list_filters_by_priority(client):
    low_resp = client.post("/api/v1/tasks", json={"title": "Low priority", "priority": "LOW"})
    critical_resp = client.post(
        "/api/v1/tasks", json={"title": "Critical priority", "priority": "CRITICAL"}
    )

    resp = client.get("/api/v1/tasks", params={"priority": "CRITICAL"})
    ids = [t["id"] for t in resp.json()]
    assert critical_resp.json()["id"] in ids
    assert low_resp.json()["id"] not in ids

    client.delete(f"/api/v1/tasks/{low_resp.json()['id']}")
    client.delete(f"/api/v1/tasks/{critical_resp.json()['id']}")


def test_overdue_filter(client):
    overdue_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Overdue task", "due_date": "2020-01-01T00:00:00Z"},
    )
    future_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Future task", "due_date": "2099-01-01T00:00:00Z"},
    )

    resp = client.get("/api/v1/tasks", params={"overdue": True})
    ids = [t["id"] for t in resp.json()]
    assert overdue_resp.json()["id"] in ids
    assert future_resp.json()["id"] not in ids

    client.delete(f"/api/v1/tasks/{overdue_resp.json()['id']}")
    client.delete(f"/api/v1/tasks/{future_resp.json()['id']}")


def test_completing_an_overdue_task_removes_it_from_overdue_filter(client):
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Overdue then done", "due_date": "2020-01-01T00:00:00Z"},
    )
    task_id = resp.json()["id"]

    client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"})

    resp = client.get("/api/v1/tasks", params={"overdue": True})
    ids = [t["id"] for t in resp.json()]
    assert task_id not in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_update_task(client):
    resp = client.post("/api/v1/tasks", json={"title": "Original title"})
    task_id = resp.json()["id"]

    resp = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated title", "priority": "HIGH", "due_date_provided": False},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"
    assert resp.json()["priority"] == "HIGH"

    client.delete(f"/api/v1/tasks/{task_id}")


def test_valid_status_transition(client):
    resp = client.post("/api/v1/tasks", json={"title": "Transition test"})
    task_id = resp.json()["id"]

    resp = client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "IN_PROGRESS"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"

    resp = client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"
    assert resp.json()["completed_at"] is not None

    client.delete(f"/api/v1/tasks/{task_id}")


def test_invalid_status_transition_from_done_is_rejected(client):
    resp = client.post("/api/v1/tasks", json={"title": "Terminal state test"})
    task_id = resp.json()["id"]
    client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"})

    resp = client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "TODO"})
    assert resp.status_code == 422
    assert resp.json()["error"] == "validation_error"

    client.delete(f"/api/v1/tasks/{task_id}")


def test_delete_task_then_404(client):
    resp = client.post("/api/v1/tasks", json={"title": "To be deleted"})
    task_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 404


def test_search_finds_matching_task(client):
    resp = client.post(
        "/api/v1/tasks", json={"title": "Renew passport", "description": "Before travel in June"}
    )
    task_id = resp.json()["id"]

    resp = client.get("/api/v1/tasks/search", params={"q": "passport"})
    assert resp.status_code == 200
    ids = [t["id"] for t in resp.json()]
    assert task_id in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_get_nonexistent_task_is_404(client):
    resp = client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
