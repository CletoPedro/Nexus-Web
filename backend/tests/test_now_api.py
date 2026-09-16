"""
NOW dashboard API tests, run against the real Postgres database. Confirms
aggregation, overdue/high-priority/upcoming classification, and recency
ordering for Memory/Documents/Inventory/Timeline.
"""
from datetime import UTC, datetime, timedelta





def _iso(dt: datetime) -> str:
    return dt.isoformat()


def test_overdue_task_appears_in_overdue_section(client):
    past = _iso(datetime.now(UTC) - timedelta(days=3))
    resp = client.post("/api/v1/tasks", json={"title": "Overdue NOW test", "due_date": past})
    task_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now")
    assert now_resp.status_code == 200
    ids = [t["id"] for t in now_resp.json()["overdue_tasks"]]
    assert task_id in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_completed_overdue_task_is_excluded(client):
    past = _iso(datetime.now(UTC) - timedelta(days=3))
    resp = client.post(
        "/api/v1/tasks", json={"title": "Completed overdue NOW test", "due_date": past}
    )
    task_id = resp.json()["id"]
    client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "DONE"})

    now_resp = client.get("/api/v1/now")
    ids = [t["id"] for t in now_resp.json()["overdue_tasks"]]
    assert task_id not in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_high_priority_task_appears_in_high_priority_section(client):
    resp = client.post(
        "/api/v1/tasks", json={"title": "Critical NOW test", "priority": "CRITICAL"}
    )
    task_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now")
    ids = [t["id"] for t in now_resp.json()["high_priority_tasks"]]
    assert task_id in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_low_priority_task_does_not_appear_in_high_priority_section(client):
    resp = client.post("/api/v1/tasks", json={"title": "Low priority NOW test", "priority": "LOW"})
    task_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now")
    ids = [t["id"] for t in now_resp.json()["high_priority_tasks"]]
    assert task_id not in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_overdue_high_priority_task_appears_only_in_overdue_not_duplicated(client):
    past = _iso(datetime.now(UTC) - timedelta(days=1))
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Overdue+critical NOW test", "priority": "CRITICAL", "due_date": past},
    )
    task_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now").json()
    assert task_id in [t["id"] for t in now_resp["overdue_tasks"]]
    assert task_id not in [t["id"] for t in now_resp["high_priority_tasks"]]

    client.delete(f"/api/v1/tasks/{task_id}")


def test_upcoming_task_within_window_appears_in_upcoming_section(client):
    soon = _iso(datetime.now(UTC) + timedelta(days=2))
    resp = client.post("/api/v1/tasks", json={"title": "Upcoming NOW test", "due_date": soon})
    task_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now", params={"upcoming_days": 7})
    ids = [t["id"] for t in now_resp.json()["upcoming_tasks"]]
    assert task_id in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_far_future_task_excluded_from_upcoming_window(client):
    far = _iso(datetime.now(UTC) + timedelta(days=60))
    resp = client.post("/api/v1/tasks", json={"title": "Far future NOW test", "due_date": far})
    task_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now", params={"upcoming_days": 7})
    ids = [t["id"] for t in now_resp.json()["upcoming_tasks"]]
    assert task_id not in ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_recent_memory_reflects_latest_creation(client):
    resp = client.post("/api/v1/memories", json={"content": "Most recent NOW test memory"})
    memory_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now", params={"recent_limit": 3})
    ids = [m["id"] for m in now_resp.json()["recent_memories"]]
    assert memory_id in ids

    client.delete(f"/api/v1/memories/{memory_id}")


def test_recent_documents_and_inventory_reflect_latest_creation(client):
    doc = client.post("/api/v1/documents", json={"title": "Recent NOW test doc"})
    item = client.post("/api/v1/inventory", json={"name": "Recent NOW test item"})

    now_resp = client.get("/api/v1/now", params={"recent_limit": 3}).json()
    assert doc.json()["id"] in [d["id"] for d in now_resp["recent_documents"]]
    assert item.json()["id"] in [i["id"] for i in now_resp["recent_inventory"]]

    client.delete(f"/api/v1/documents/{doc.json()['id']}")
    client.delete(f"/api/v1/inventory/{item.json()['id']}")


def test_recent_timeline_reflects_new_events(client):
    resp = client.post("/api/v1/memories", json={"content": "NOW timeline test memory"})
    memory_id = resp.json()["id"]

    now_resp = client.get("/api/v1/now", params={"recent_limit": 5})
    entity_ids = [e["entity_id"] for e in now_resp.json()["recent_timeline"]]
    assert memory_id in entity_ids

    client.delete(f"/api/v1/memories/{memory_id}")


def test_recent_limit_is_respected(client):
    created = []
    for i in range(4):
        resp = client.post("/api/v1/memories", json={"content": f"NOW limit test {i}"})
        created.append(resp.json()["id"])

    now_resp = client.get("/api/v1/now", params={"recent_limit": 2})
    assert len(now_resp.json()["recent_memories"]) == 2

    for cid in created:
        client.delete(f"/api/v1/memories/{cid}")
