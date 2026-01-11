import bentoml
from bentoml import Service, Runnable, Runner

from bentoml.io import JSON
import numpy as np

import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

# Charger modèles
model = bentoml.sklearn.load_model("linear_regression_model:latest")
scaler = bentoml.sklearn.load_model("data_scaler:latest")

# JWT config
JWT_SECRET_KEY = "BentoMLSecretKey"
JWT_ALGORITHM = "HS256"

USERS = {
    "LawrenceBENE": "BentoMlTop",
}

def create_jwt_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": user_id, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# Décorateur JWT compatible legacy
def require_jwt(func):
    def wrapper(payload, context):
        auth = context.request.headers.get("Authorization")
        if not auth:
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        try:
            token = auth.split()[1]
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        return func(payload)
    return wrapper

# Runnable
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

# Runner
admission_runner = Runner(AdmissionRunnable, name="admission_runner")

# Service
svc = Service("admission_api", runners=[admission_runner])

# LOGIN endpoint
@svc.api(input=JSON(), output=JSON(), route="/login")
def login(credentials):
    username = credentials.get("username")
    password = credentials.get("password")

    if username in USERS and USERS[username] == password:
        return {"token": create_jwt_token(username)}

    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

# PREDICT endpoint (protégé)
@svc.api(input=JSON(), output=JSON(), route="/predict")
@require_jwt
def predict(payload):
    features = np.array([[
        payload["GRE Score"],
        payload["TOEFL Score"],
        payload["University Rating"],
        payload["SOP"],
        payload["LOR"],
        payload["CGPA"],
        payload["Research"]
    ]])

    prediction = admission_runner.predict.run(features)

    value = prediction
    if hasattr(value, "tolist"):
        value = value.tolist()
    while isinstance(value, list):
        value = value[0]

    return {"chance_of_admit": float(value)}
