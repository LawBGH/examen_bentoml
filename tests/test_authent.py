import os
os.environ["BENTOML_DISABLE_METRICS"] = "true"

import jwt
import time
from src.service import JWT_SECRET_KEY, JWT_ALGORITHM, create_jwt_token


def test_invalid_token():
    try:
        jwt.decode("invalid.token", JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert False
    except Exception:
        assert True


def test_expired_token():
    expired_payload = {
        "sub": "LawrenceBENE",
        "exp": int(time.time()) - 10  # expiré
    }
    expired_token = jwt.encode(expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    try:
        jwt.decode(expired_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert False
    except Exception:
        assert True


def test_valid_token():
    token = create_jwt_token("LawrenceBENE")
    decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["sub"] == "LawrenceBENE"
