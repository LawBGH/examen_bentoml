import os
os.environ["BENTOML_DISABLE_METRICS"] = "true"

import bentoml
from bentoml import Service, Runner, Runnable
from bentoml.io import JSON

import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


# -----------------------------
# MODELS
# -----------------------------
model = bentoml.sklearn.load_model("linear_regression_model:latest")
scaler = bentoml.sklearn.load_model("data_scaler:latest")


# -----------------------------
# JWT CONFIG
# -----------------------------
JWT_SECRET_KEY = "BentoMLSecretKey"
JWT_ALGORITHM = "HS256"

USERS = {
    "LawrenceBENE": "BentoMlTop"
}

def create_jwt_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


# -----------------------------
# INPUT MODEL
# -----------------------------
class PredictInput(BaseModel):
    GRE_Score: float = Field(..., alias="GRE Score")
    TOEFL_Score: float = Field(..., alias="TOEFL Score")
    University_Rating: int = Field(..., alias="University Rating")
    SOP: float
    LOR: float
    CGPA: float
    Research: int


# -----------------------------
# RUNNABLE
# -----------------------------
class AdmissionRunnable(Runnable):
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self):
        self.model = model
        self.scaler = scaler

    @Runnable.method(batchable=True)
    def predict(self, arr):
        scaled = self.scaler.transform(arr)
        return self.model.predict(scaled)


runner = Runner(AdmissionRunnable, name="admission_runner")


# -----------------------------
# SERVICE
# -----------------------------
svc = Service("admission_api", runners=[runner])


# -----------------------------
# LOGIN
# -----------------------------
@svc.api(input=JSON(), output=JSON(), route="/login")
def login(credentials):
    if not isinstance(credentials, dict):
        return {"detail": "Invalid JSON"}, 400

    username = credentials.get("username")
    password = credentials.get("password")

    if username in USERS and USERS[username] == password:
        return {"token": create_jwt_token(username)}

    return {"detail": "Invalid credentials"}, 401

# PREDICT 
# -----------------------------
@svc.api(input=JSON(pydantic_model=PredictInput), output=JSON(), route="/predict")
def predict(input_data, context):

    # Vérification JWT
    auth = context.request.headers.get("Authorization")
    if not auth:
        return {"detail": "Missing token"}, 401

    try:
        token = auth.split()[1]
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        return {"detail": "Invalid or expired token"}, 401

    # Extraction des features
    features = [
        input_data.GRE_Score,
        input_data.TOEFL_Score,
        input_data.University_Rating,
        input_data.SOP,
        input_data.LOR,
        input_data.CGPA,
        input_data.Research,
    ]

    # Prédiction
    pred = runner.predict.run([features])

    if hasattr(pred, "result"):
        pred = pred.result()

    if hasattr(pred, "tolist"):
        pred = pred.tolist()

    while isinstance(pred, list):
        pred = pred[0]

    return {"chance_of_admit": float(pred)}
