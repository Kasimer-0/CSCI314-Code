import pytest
from fastapi.testclient import TestClient
import sys
import os

#Make sure Python can find main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app 

# Create a test client
client_fixture = TestClient(app)

@pytest.fixture
def client():
    return client_fixture

# --- Test code ---

def test_fundraiser_login_success(client):
    payload = {
        "email": "test@example.com",
        "password": "securepassword"
    }

    # Note: Please ensure that your main.py file actually contains the route @app.post("/fundraisers/login").
    response = client.post("/fundraisers/login", json=payload)

    assert response.status_code == 200, \
        f"Expected 200 but got {response.status_code}"

    data = response.json()
    assert "access_token" in data, "Missing access token"
    assert data["token_type"] == "bearer"
