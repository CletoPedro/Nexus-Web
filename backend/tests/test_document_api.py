"""Document API tests, run against the real Postgres database."""




def test_create_and_get_document(client):
    resp = client.post(
        "/api/v1/documents",
        json={"title": "Passport", "category": "identity", "file_name": "passport.pdf"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Passport"
    assert body["category"] == "identity"

    doc_id = body["id"]
    resp = client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 200

    client.delete(f"/api/v1/documents/{doc_id}")


def test_create_rejects_empty_title(client):
    resp = client.post("/api/v1/documents", json={"title": "  "})
    assert resp.status_code == 422


def test_storage_path_is_metadata_only(client):
    """
    Confirms storage_path is accepted and stored as a plain string, with
    no attempt to read/validate/serve an actual file — per the explicit
    W7 scope limitation (no real file storage in this phase).
    """
    resp = client.post(
        "/api/v1/documents",
        json={"title": "Warranty", "storage_path": "/does/not/exist/on/any/disk.pdf"},
    )
    assert resp.status_code == 201
    assert resp.json()["storage_path"] == "/does/not/exist/on/any/disk.pdf"
    client.delete(f"/api/v1/documents/{resp.json()['id']}")


def test_list_filters_by_category(client):
    id_resp = client.post("/api/v1/documents", json={"title": "Citizen Card", "category": "identity"})
    contract_resp = client.post("/api/v1/documents", json={"title": "Lease", "category": "contract"})

    resp = client.get("/api/v1/documents", params={"category": "identity"})
    ids = [d["id"] for d in resp.json()]
    assert id_resp.json()["id"] in ids
    assert contract_resp.json()["id"] not in ids

    client.delete(f"/api/v1/documents/{id_resp.json()['id']}")
    client.delete(f"/api/v1/documents/{contract_resp.json()['id']}")


def test_update_document(client):
    resp = client.post("/api/v1/documents", json={"title": "Old title"})
    doc_id = resp.json()["id"]

    resp = client.put(f"/api/v1/documents/{doc_id}", json={"title": "New title", "category": "manual"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    assert resp.json()["category"] == "manual"

    client.delete(f"/api/v1/documents/{doc_id}")


def test_delete_document_then_404(client):
    resp = client.post("/api/v1/documents", json={"title": "To delete"})
    doc_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 404


def test_search_finds_matching_document(client):
    resp = client.post(
        "/api/v1/documents",
        json={"title": "Car Insurance Policy", "description": "Renews every January"},
    )
    doc_id = resp.json()["id"]

    resp = client.get("/api/v1/documents/search", params={"q": "insurance"})
    ids = [d["id"] for d in resp.json()]
    assert doc_id in ids

    client.delete(f"/api/v1/documents/{doc_id}")


def test_get_nonexistent_document_is_404(client):
    resp = client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
