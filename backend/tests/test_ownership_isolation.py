"""
Cross-user ownership isolation tests. The central security requirement
of W12: "User A nunca pode consultar Memory/Task/Document/Inventory de
User B." Run against two real, independently-authenticated users and a
real database — not mocked.
"""


def test_user_cannot_get_another_users_memory(client, other_client):
    resp = client.post("/api/v1/memories", json={"content": "User A's private memory"})
    memory_id = resp.json()["id"]

    other_resp = other_client.get(f"/api/v1/memories/{memory_id}")
    assert other_resp.status_code == 404  # not 403 — existence is not revealed either

    client.delete(f"/api/v1/memories/{memory_id}")


def test_user_list_never_includes_another_users_memories(client, other_client):
    resp = client.post("/api/v1/memories", json={"content": "Only User A should see this"})
    memory_id = resp.json()["id"]

    other_list = other_client.get("/api/v1/memories").json()
    assert memory_id not in [m["id"] for m in other_list]

    client.delete(f"/api/v1/memories/{memory_id}")


def test_user_cannot_update_another_users_memory(client, other_client):
    resp = client.post("/api/v1/memories", json={"content": "Original by User A"})
    memory_id = resp.json()["id"]

    other_resp = other_client.put(
        f"/api/v1/memories/{memory_id}", json={"content": "Hijacked by User B"}
    )
    assert other_resp.status_code == 404

    # Confirm the content was NOT changed.
    check = client.get(f"/api/v1/memories/{memory_id}")
    assert check.json()["content"] == "Original by User A"

    client.delete(f"/api/v1/memories/{memory_id}")


def test_user_cannot_delete_another_users_memory(client, other_client):
    resp = client.post("/api/v1/memories", json={"content": "User A memory, do not delete"})
    memory_id = resp.json()["id"]

    other_client.delete(f"/api/v1/memories/{memory_id}")

    # Still there, still visible to its real owner.
    check = client.get(f"/api/v1/memories/{memory_id}")
    assert check.status_code == 200

    client.delete(f"/api/v1/memories/{memory_id}")


def test_user_search_never_returns_another_users_data(client, other_client):
    marker = "crossuserisolationmarker"
    resp = client.post("/api/v1/memories", json={"content": f"{marker} belongs to user A"})
    memory_id = resp.json()["id"]

    other_search = other_client.get("/api/v1/memories/search", params={"q": marker}).json()
    assert memory_id not in [m["id"] for m in other_search]

    client.delete(f"/api/v1/memories/{memory_id}")


def test_isolation_holds_across_all_four_modules(client, other_client):
    mem = client.post("/api/v1/memories", json={"content": "Isolation test memory"})
    task = client.post("/api/v1/tasks", json={"title": "Isolation test task"})
    doc = client.post("/api/v1/documents", json={"title": "Isolation test doc"})
    item = client.post("/api/v1/inventory", json={"name": "Isolation test item"})

    assert other_client.get(f"/api/v1/memories/{mem.json()['id']}").status_code == 404
    assert other_client.get(f"/api/v1/tasks/{task.json()['id']}").status_code == 404
    assert other_client.get(f"/api/v1/documents/{doc.json()['id']}").status_code == 404
    assert other_client.get(f"/api/v1/inventory/{item.json()['id']}").status_code == 404

    client.delete(f"/api/v1/memories/{mem.json()['id']}")
    client.delete(f"/api/v1/tasks/{task.json()['id']}")
    client.delete(f"/api/v1/documents/{doc.json()['id']}")
    client.delete(f"/api/v1/inventory/{item.json()['id']}")


def test_user_cannot_link_inventory_to_another_users_document(client, other_client):
    """
    A user must not be able to reference another user's document_id, even
    though it's a valid, existing document — just not theirs.
    """
    other_doc = other_client.post("/api/v1/documents", json={"title": "User B's document"})
    other_doc_id = other_doc.json()["id"]

    resp = client.post(
        "/api/v1/inventory",
        json={"name": "Trying to link cross-user", "document_id": other_doc_id},
    )
    assert resp.status_code == 422

    other_client.delete(f"/api/v1/documents/{other_doc_id}")


def test_timeline_isolated_per_user(client, other_client):
    marker = "timelineisolationmarker"
    resp = client.post("/api/v1/memories", json={"content": marker})
    memory_id = resp.json()["id"]

    other_timeline = other_client.get("/api/v1/timeline", params={"limit": 500}).json()
    assert memory_id not in [e["entity_id"] for e in other_timeline]

    client.delete(f"/api/v1/memories/{memory_id}")


def test_now_dashboard_isolated_per_user(client, other_client):
    resp = client.post("/api/v1/tasks", json={"title": "User A NOW isolation task"})
    task_id = resp.json()["id"]

    other_now = other_client.get("/api/v1/now").json()
    all_other_task_ids = [
        t["id"]
        for section in ("overdue_tasks", "high_priority_tasks", "upcoming_tasks")
        for t in other_now[section]
    ]
    assert task_id not in all_other_task_ids

    client.delete(f"/api/v1/tasks/{task_id}")


def test_global_search_isolated_per_user(client, other_client):
    marker = "globalsearchisolationmarker"
    resp = client.post("/api/v1/memories", json={"content": marker})
    memory_id = resp.json()["id"]

    other_search = other_client.get("/api/v1/search", params={"q": marker}).json()
    assert other_search["total"] == 0

    client.delete(f"/api/v1/memories/{memory_id}")
