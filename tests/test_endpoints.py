import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_add_points(client):
    response = client.post('/add', json={
        "payer": "DANNON",
        "points": 300,
        "timestamp": "2022-10-31T10:00:00Z"
    })
    assert response.status_code == 200

def test_get_balance(client):
    response = client.get('/balance')
    assert response.status_code == 200
    assert "DANNON" in response.json
