import os
from src.service import create_jwt_token

VALID_INPUT = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.0,
    "CGPA": 9.2,
    "Research": 1
}


def test_predict_missing_token(client):
    response = client.post("/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_predict_invalid_token(client):
    response = client.post("/predict", json=VALID_INPUT, headers={
        "Authorization": "Bearer invalid.token"
    })
    assert response.status_code == 401


def test_predict_valid_token(client):
    token = create_jwt_token("LawrenceBENE")
    response = client.post("/predict", json=VALID_INPUT, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
   


def test_predict_invalid_input(client):
    token = create_jwt_token("LawrenceBENE")
    response = client.post("/predict", json={"bad": "data"}, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code in (400, 422)
