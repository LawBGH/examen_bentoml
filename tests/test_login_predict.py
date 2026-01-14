import os
from src.service import create_jwt_token

def test_login_success(client):
    response = client.post("/login", json={
        "username": "LawrenceBENE",
        "password": "BentoMlTop"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(client):
    response = client.post("/login", json={
        "username": "WrongUser",
        "password": "WrongPass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

