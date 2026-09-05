"""
Timeline API tests, run against the real Postgres database. Includes
integration tests confirming Memory, Tasks, Documents, and Inventory each
generate a real timeline event on creation (and Tasks on completion) —
this is the central requirement of W9.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _find_event(events: list[dict], entity_id: str, event_type: str) -> dict | None:
    for e in events:
        if e["entity_id"] == entity_id and e["event_type"] == event_type:
            return e
    return None


def test_memory_creation_generates_timeline_event():
    resp = client.post("/api/v1/memories", json={"content": "Timeline integration test memory"})
    memory_id = resp.json()["id"]

    resp = client.get("/api/v1/timeline", params={"event_type": "MEMORY_CREATED", "limit": 200})
    assert resp.status_code == 200
    event = _find_event(resp.json(), memory_id, "MEMORY_CREATED")
    assert event is not None
    assert event["entity_type"] == "memory"

    client.delete(f"/api/v1/memories/{memory_id}")


def test_task_creation_generates_timeline_event():
    resp = client.post("/api/v1/tasks", json={"title": "Timeline integration test task"})
    task_id = resp.json()["id"]

    resp = client.get("/api/v1/timeline", params={"event_type": "TASK_CREATED", "limit": 200})
    event = _find_event(resp.json(), task_id, "TASK_CREATED")
    assert event is not None

    client.delete(f"/api/v1/tasks/{task_id}")


def test_task_completion_generates_timeline_event():
    resp = client.post("/api/v1/tasks", json={"title": "Task to complete"})
    task_id = resp.json()["id"]

    client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"})

    resp = client.get("/api/v1/timeline", params={"event_type": "TASK_COMPLETED", "limit": 200})
    event = _find_event(resp.json(), task_id, "TASK_COMPLETED")
    assert event is not None

    client.delete(f"/api/v1/tasks/{task_id}")


def test_task_creation_and_completion_both_recorded_separately():
    """A single task generates two distinct timeline events, not one."""
    resp = client.post("/api/v1/tasks", json={"title": "Both events test"})
    task_id = resp.json()["id"]
    client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"})

    resp = client.get("/api/v1/timeline", params={"limit": 500})
    events = [e for e in resp.json() if e["entity_id"] == task_id]
    types = {e["event_type"] for e in events}
    assert "TASK_CREATED" in types
    assert "TASK_COMPLETED" in types
    assert len(events) == 2

    client.delete(f"/api/v1/tasks/{task_id}")


def test_document_creation_generates_timeline_event():
    resp = client.post("/api/v1/documents", json={"title": "Timeline integration test doc"})
    doc_id = resp.json()["id"]

    resp = client.get("/api/v1/timeline", params={"event_type": "DOCUMENT_CREATED", "limit": 200})
    event = _find_event(resp.json(), doc_id, "DOCUMENT_CREATED")
    assert event is not None

    client.delete(f"/api/v1/documents/{doc_id}")


def test_inventory_creation_generates_timeline_event():
    resp = client.post("/api/v1/inventory", json={"name": "Timeline integration test item"})
    item_id = resp.json()["id"]

    resp = client.get("/api/v1/timeline", params={"event_type": "INVENTORY_CREATED", "limit": 200})
    event = _find_event(resp.json(), item_id, "INVENTORY_CREATED")
    assert event is not None

    client.delete(f"/api/v1/inventory/{item_id}")


def test_inventory_update_generates_timeline_event():
    resp = client.post("/api/v1/inventory", json={"name": "Update test item"})
    item_id = resp.json()["id"]

    client.put(f"/api/v1/inventory/{item_id}", json={"name": "Update test item", "quantity": 5})

    resp = client.get("/api/v1/timeline", params={"event_type": "INVENTORY_UPDATED", "limit": 200})
    event = _find_event(resp.json(), item_id, "INVENTORY_UPDATED")
    assert event is not None

    client.delete(f"/api/v1/inventory/{item_id}")


def test_timeline_ordered_newest_first():
    resp1 = client.post("/api/v1/memories", json={"content": "First timeline order test"})
    resp2 = client.post("/api/v1/memories", json={"content": "Second timeline order test"})

    resp = client.get("/api/v1/timeline", params={"event_type": "MEMORY_CREATED", "limit": 5})
    events = resp.json()
    ids_in_order = [e["entity_id"] for e in events]
    assert ids_in_order.index(resp2.json()["id"]) < ids_in_order.index(resp1.json()["id"])

    client.delete(f"/api/v1/memories/{resp1.json()['id']}")
    client.delete(f"/api/v1/memories/{resp2.json()['id']}")


def test_timeline_search():
    resp = client.post(
        "/api/v1/memories", json={"content": "Renew car insurance before it lapses"}
    )
    memory_id = resp.json()["id"]

    resp = client.get("/api/v1/timeline/search", params={"q": "insurance"})
    ids = [e["entity_id"] for e in resp.json()]
    assert memory_id in ids

    client.delete(f"/api/v1/memories/{memory_id}")
