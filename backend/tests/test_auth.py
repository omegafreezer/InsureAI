from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login():
    response = client.post('/api/auth/login', json={'username': 'admin', 'password': 'Admin@123'})
    assert response.status_code == 200
    assert 'access_token' in response.json()
