def test_read_root(client):
    """Kiểm tra endpoint root / trả về thông báo 200"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_health_check(client):
    """Kiểm tra endpoint /health phục vụ Docker HEALTHCHECK và Zero-downtime deploy"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-management-api"
    assert "version" in data
