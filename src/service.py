import bentoml
from bentoml import Service, Runnable, Runner
from bentoml.io import JSON

import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field

# -----------------------------
# Pydantic input validation
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
# Load models
# -----------------------------
model = bentoml.sklearn.load_model("linear_regression_model:latest")
scaler = bentoml.sklearn.load_model("data_scaler:latest")

# -----------------------------
# JWT config
# -----------------------------
JWT_SECRET_KEY = "BentoMLSecretKey"
JWT_ALGORITHM = "HS256"

USERS = {
    "LawrenceBENE": "BentoMlTop",
}

def create_jwt_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": user_id, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# -----------------------------
# JWT middleware
# -----------------------------
def require_jwt(func):
    def wrapper(input_data, context):
        auth = context.request.headers.get("Authorization")
        if not auth:
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        try:
            token = auth.split()[1]
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        return func(input_data)
    return wrapper

# -----------------------------
# Runnable
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

admission_runner = Runner(AdmissionRunnable, name="admission_runner")

# -----------------------------
# Service
# -----------------------------
svc = Service("admission_api", runners=[admission_runner])

# -----------------------------
# LOGIN
# -----------------------------
@svc.api(input=JSON(), output=JSON(), route="/login")
def login(credentials):
    if not isinstance(credentials, dict):
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON"})

    username = credentials.get("username")
    password = credentials.get("password")

    if username in USERS and USERS[username] == password:
        return {"token": create_jwt_token(username)}

    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

# -----------------------------
# PREDICT 
# -----------------------------
@svc.api(input=JSON(pydantic_model=PredictInput), output=JSON(), route="/predict")
@require_jwt
def predict(input_data: PredictInput):
    features = [
        input_data.GRE_Score,
        input_data.TOEFL_Score,
        input_data.University_Rating,
        input_data.SOP,
        input_data.LOR,
        input_data.CGPA,
        input_data.Research,
    ]

    prediction = admission_runner.predict.run([features])

    # Résolution du résultat (Future, WorkerResult, ndarray, list…)
    if hasattr(prediction, "result"):
        prediction = prediction.result()

    if hasattr(prediction, "tolist"):
        prediction = prediction.tolist()

    while isinstance(prediction, list):
        prediction = prediction[0]

    return {"chance_of_admit": float(prediction)}
