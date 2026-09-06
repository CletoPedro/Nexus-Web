"""Inventory API tests, run against the real Postgres database."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_item():
    resp = client.post("/api/v1/inventory", json={"name": "Laptop", "location": "office"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Laptop"
    assert body["quantity"] == 1

    item_id = body["id"]
    resp = client.get(f"/api/v1/inventory/{item_id}")
    assert resp.status_code == 200

    client.delete(f"/api/v1/inventory/{item_id}")


def test_create_rejects_empty_name():
    resp = client.post("/api/v1/inventory", json={"name": "  "})
    assert resp.status_code == 422


def test_create_rejects_negative_quantity():
    resp = client.post("/api/v1/inventory", json={"name": "Widget", "quantity": -1})
    assert resp.status_code == 422


def test_create_with_valid_document_reference():
    doc_resp = client.post("/api/v1/documents", json={"title": "Laptop Warranty"})
    doc_id = doc_resp.json()["id"]

    resp = client.post(
        "/api/v1/inventory",
        json={"name": "Laptop", "document_id": doc_id},
    )
    assert resp.status_code == 201
    assert resp.json()["document_id"] == doc_id

    client.delete(f"/api/v1/inventory/{resp.json()['id']}")
    client.delete(f"/api/v1/documents/{doc_id}")


def test_create_rejects_nonexistent_document_reference():
    resp = client.post(
        "/api/v1/inventory",
        json={"name": "Laptop", "document_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 422
    assert resp.json()["error"] == "validation_error"


def test_list_filters_by_category_and_location():
    tool_resp = client.post(
        "/api/v1/inventory", json={"name": "Drill", "category": "tools", "location": "garage"}
    )
    furniture_resp = client.post(
        "/api/v1/inventory", json={"name": "Desk", "category": "furniture", "location": "office"}
    )

    resp = client.get("/api/v1/inventory", params={"category": "tools"})
    ids = [i["id"] for i in resp.json()]
    assert tool_resp.json()["id"] in ids
    assert furniture_resp.json()["id"] not in ids

    resp = client.get("/api/v1/inventory", params={"location": "office"})
    ids = [i["id"] for i in resp.json()]
    assert furniture_resp.json()["id"] in ids
    assert tool_resp.json()["id"] not in ids

    client.delete(f"/api/v1/inventory/{tool_resp.json()['id']}")
    client.delete(f"/api/v1/inventory/{furniture_resp.json()['id']}")


def test_update_item():
    resp = client.post("/api/v1/inventory", json={"name": "Old name"})
    item_id = resp.json()["id"]

    resp = client.put(f"/api/v1/inventory/{item_id}", json={"name": "New name", "quantity": 3})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New name"
    assert resp.json()["quantity"] == 3

    client.delete(f"/api/v1/inventory/{item_id}")


def test_delete_item_then_404():
    resp = client.post("/api/v1/inventory", json={"name": "To delete"})
    item_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/inventory/{item_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/inventory/{item_id}")
    assert resp.status_code == 404


def test_search_finds_matching_item():
    resp = client.post(
        "/api/v1/inventory", json={"name": "HDMI cable", "location": "blue drawer"}
    )
    item_id = resp.json()["id"]

    resp = client.get("/api/v1/inventory/search", params={"q": "HDMI"})
    ids = [i["id"] for i in resp.json()]
    assert item_id in ids

    client.delete(f"/api/v1/inventory/{item_id}")


def test_get_nonexistent_item_is_404():
    resp = client.get("/api/v1/inventory/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
