"""
Confirms every data endpoint requires authentication — "Nenhum endpoint
de dados deve permanecer publicamente acessível sem autenticação." Run
against the real app, real routing, no mocking.
"""
import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/v1/memories"),
        ("POST", "/api/v1/memories"),
        ("GET", "/api/v1/memories/search?q=x"),
        ("GET", "/api/v1/tasks"),
        ("POST", "/api/v1/tasks"),
        ("GET", "/api/v1/tasks/search?q=x"),
        ("GET", "/api/v1/documents"),
        ("POST", "/api/v1/documents"),
        ("GET", "/api/v1/documents/search?q=x"),
        ("GET", "/api/v1/inventory"),
        ("POST", "/api/v1/inventory"),
        ("GET", "/api/v1/inventory/search?q=x"),
        ("GET", "/api/v1/timeline"),
        ("GET", "/api/v1/timeline/search?q=x"),
        ("GET", "/api/v1/search?q=x"),
        ("GET", "/api/v1/now"),
    ],
)
def test_data_endpoint_requires_authentication(anon_client, method, path):
    resp = anon_client.request(method, path, json={} if method == "POST" else None)
    assert resp.status_code == 401, f"{method} {path} should require auth, got {resp.status_code}"


def test_health_endpoints_remain_public(anon_client):
    """Health checks must stay reachable for deployment platforms without a session."""
    assert anon_client.get("/health").status_code == 200
    assert anon_client.get("/health/db").status_code == 200
