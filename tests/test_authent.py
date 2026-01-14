import requests
from src.service import create_jwt_token

BASE_URL = "http://localhost:3000"

VALID_INPUT = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.0,
    "CGPA": 9.2,
    "Research": 1
}

def test_predict_missing_token():
    r = requests.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert r.status_code == 401

def test_predict_invalid_token():
    r = requests.post(
        f"{BASE_URL}/predict",
        json=VALID_INPUT,
        headers={"Authorization": "Bearer invalid.token"}
    )
    assert r.status_code == 401

def test_predict_valid_token():
    # on a importé plus haut la fonction create_jwt_token pour générer un token valide à partir de la même secret key
    # Il n'y a donc pas besoin d'un mot de passe.
    token = create_jwt_token("LawrenceBENE")
    r = requests.post(
        f"{BASE_URL}/predict",
        json=VALID_INPUT,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
