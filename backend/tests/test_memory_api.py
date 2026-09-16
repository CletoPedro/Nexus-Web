"""
Memory API tests. These run against the real Postgres database configured
in Settings — no mocking of the repository or database layer. Each test
cleans up the rows it creates.
"""




def test_create_and_get_memory(client):
    resp = client.post("/api/v1/memories", json={"content": "Passport is in the safe."})
    assert resp.status_code == 201
    body = resp.json()
    assert body["content"] == "Passport is in the safe."
    assert body["tags"] == []

    memory_id = body["id"]
    resp = client.get(f"/api/v1/memories/{memory_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == memory_id

    client.delete(f"/api/v1/memories/{memory_id}")


def test_create_rejects_empty_content(client):
    resp = client.post("/api/v1/memories", json={"content": "   "})
    assert resp.status_code == 422


def test_list_memories_includes_created(client):
    resp = client.post("/api/v1/memories", json={"content": "List-test memory."})
    memory_id = resp.json()["id"]

    resp = client.get("/api/v1/memories")
    assert resp.status_code == 200
    ids = [m["id"] for m in resp.json()]
    assert memory_id in ids

    client.delete(f"/api/v1/memories/{memory_id}")


def test_update_memory(client):
    resp = client.post("/api/v1/memories", json={"content": "Original content."})
    memory_id = resp.json()["id"]

    resp = client.put(
        f"/api/v1/memories/{memory_id}",
        json={"content": "Updated content.", "tags": ["important"]},
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == "Updated content."
    assert resp.json()["tags"] == ["important"]

    client.delete(f"/api/v1/memories/{memory_id}")


def test_delete_memory_then_404(client):
    resp = client.post("/api/v1/memories", json={"content": "To be deleted."})
    memory_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/memories/{memory_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/memories/{memory_id}")
    assert resp.status_code == 404


def test_search_finds_matching_memory(client):
    resp = client.post(
        "/api/v1/memories", json={"content": "My HDMI cable is in the blue drawer."}
    )
    memory_id = resp.json()["id"]

    resp = client.get("/api/v1/memories/search", params={"q": "HDMI cable"})
    assert resp.status_code == 200
    ids = [m["id"] for m in resp.json()]
    assert memory_id in ids

    client.delete(f"/api/v1/memories/{memory_id}")


def test_get_nonexistent_memory_is_404(client):
    resp = client.get("/api/v1/memories/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
