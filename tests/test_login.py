import os
os.environ["BENTOML_DISABLE_METRICS"] = "true"

from starlette.testclient import TestClient
from src.service import svc

def get_client():
    return TestClient(svc.asgi_app)


def test_login_success():
    client = get_client()
    response = client.post("/login", json={
        "username": "LawrenceBENE",
        "password": "BentoMlTop"
    })
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_invalid_credentials():
    client = get_client()
    response = client.post("/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 401
