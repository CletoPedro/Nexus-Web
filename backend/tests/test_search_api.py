"""
Global Search API tests, run against the real Postgres database. Confirms
cross-module results, grouping, ranking, and empty/no-results states.
"""




def test_empty_query_returns_empty_groups(client):
    resp = client.get("/api/v1/search", params={"q": ""})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["memory"] == []
    assert body["tasks"] == []
    assert body["documents"] == []
    assert body["inventory"] == []


def test_no_results_found(client):
    resp = client.get(
        "/api/v1/search", params={"q": "zzz_no_such_term_exists_anywhere_zzz"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0


def test_cross_module_search_finds_all_four_types(client):
    """
    Creates one item in each of Memory, Tasks, Documents, Inventory, all
    sharing a distinctive word, and confirms Global Search finds all four
    in a single query, correctly grouped.
    """
    marker = "xyloglossia"

    mem = client.post(
        "/api/v1/memories", json={"content": f"A note about {marker} theory."}
    )
    task = client.post(
        "/api/v1/tasks", json={"title": f"Research {marker}", "description": ""}
    )
    doc = client.post(
        "/api/v1/documents", json={"title": f"{marker} paper", "description": ""}
    )
    item = client.post(
        "/api/v1/inventory", json={"name": f"{marker} notebook", "description": ""}
    )

    resp = client.get("/api/v1/search", params={"q": marker})
    assert resp.status_code == 200
    body = resp.json()

    assert body["total"] == 4
    assert any(r["id"] == mem.json()["id"] for r in body["memory"])
    assert any(r["id"] == task.json()["id"] for r in body["tasks"])
    assert any(r["id"] == doc.json()["id"] for r in body["documents"])
    assert any(r["id"] == item.json()["id"] for r in body["inventory"])

    # Every result carries the required normalized fields.
    for group in ("memory", "tasks", "documents", "inventory"):
        for r in body[group]:
            assert set(r.keys()) >= {
                "id",
                "type",
                "title",
                "content",
                "relevance",
                "created_at",
                "target_url",
            }
            assert r["target_url"].startswith("/")

    client.delete(f"/api/v1/memories/{mem.json()['id']}")
    client.delete(f"/api/v1/tasks/{task.json()['id']}")
    client.delete(f"/api/v1/documents/{doc.json()['id']}")
    client.delete(f"/api/v1/inventory/{item.json()['id']}")


def test_results_ranked_by_relevance_descending(client):
    marker = "photosynthesis"
    weak = client.post(
        "/api/v1/memories", json={"content": f"Mentions {marker} once in passing."}
    )
    strong = client.post(
        "/api/v1/memories",
        json={"content": f"{marker} {marker} {marker} is the main subject here, {marker}."},
    )

    resp = client.get("/api/v1/search", params={"q": marker})
    memory_results = resp.json()["memory"]
    ids_in_order = [r["id"] for r in memory_results]
    assert ids_in_order.index(strong.json()["id"]) < ids_in_order.index(weak.json()["id"])

    relevances = [r["relevance"] for r in memory_results]
    assert relevances == sorted(relevances, reverse=True)

    client.delete(f"/api/v1/memories/{weak.json()['id']}")
    client.delete(f"/api/v1/memories/{strong.json()['id']}")


def test_limit_is_respected_per_module(client):
    marker = "quinoafarmstead"
    created_ids = []
    for i in range(5):
        resp = client.post("/api/v1/memories", json={"content": f"{marker} item number {i}"})
        created_ids.append(resp.json()["id"])

    resp = client.get("/api/v1/search", params={"q": marker, "limit": 2})
    assert len(resp.json()["memory"]) == 2

    for cid in created_ids:
        client.delete(f"/api/v1/memories/{cid}")


def test_search_does_not_leak_soft_deleted_items(client):
    marker = "unobtainium"
    resp = client.post("/api/v1/memories", json={"content": f"{marker} sample memory"})
    memory_id = resp.json()["id"]
    client.delete(f"/api/v1/memories/{memory_id}")

    resp = client.get("/api/v1/search", params={"q": marker})
    ids = [r["id"] for r in resp.json()["memory"]]
    assert memory_id not in ids
