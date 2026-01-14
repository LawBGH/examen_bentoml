import os


import bentoml
from bentoml import Service, Runner, Runnable
from bentoml.io import JSON

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from bentoml.exceptions import BentoMLException

import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Exception personnalisée pour les erreurs HTTP
class HTTPError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

# -----------------------------
# MODELS
# -----------------------------
print(">>> Chargement du modèle ML")
model = bentoml.sklearn.load_model("linear_regression_model:latest")
print(">>> Modèle chargé OK")

print(">>> Chargement du scaler")
scaler = bentoml.sklearn.load_model("data_scaler:latest")
print(">>> Scaler chargé OK")

# -----------------------------
# JWT CONFIG
# -----------------------------
JWT_SECRET_KEY = "BentoMLSecretKey"
JWT_ALGORITHM = "HS256"

USERS = {
    "LawrenceBENE": "BentoMlTop"
}

# -----------------------------
# MIDDLEWARE STARLETTE
# -----------------------------
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(f">>> Middleware: requête sur {request.url.path}")

        if request.url.path == "/predict":
            print(">>> Middleware: endpoint /predict détecté")
            token = request.headers.get("Authorization")
            print(f">>> Middleware: Authorization header = {token}")

            if not token:
                print(">>> Middleware: token manquant")
                return JSONResponse({"detail": "Missing authentication token"}, status_code=401)

            try:
                token = token.split()[1]
                print(f">>> Middleware: token extrait = {token}")
                jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                print(">>> Middleware: token valide")
            except Exception as e:
                print(f">>> Middleware: token invalide: {e}")
                return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)

        try:
            return await call_next(request)
        except HTTPError as e:
            return JSONResponse({"detail": e.detail}, status_code=e.status_code)

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

def create_jwt_token(user_id: str):
    print(f">>> Création du token pour user={user_id}")
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    print(f">>> Token généré = {token}")
    return token

# -----------------------------
# RUNNABLE
# -----------------------------
class AdmissionRunnable(Runnable):
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self):
        print(">>> Initialisation du Runnable")
        self.model = model
        self.scaler = scaler

    @Runnable.method(batchable=True)
    def predict(self, arr):
        print(f">>> Runnable.predict: input = {arr}")
        scaled = self.scaler.transform(arr)
        print(f">>> Runnable.predict: scaled = {scaled}")
        out = self.model.predict(scaled)
        print(f">>> Runnable.predict: output = {out}")
        return out

runner = Runner(AdmissionRunnable, name="admission_runner")

# -----------------------------
# SERVICE
# -----------------------------
print(">>> Initialisation du service BentoML")
svc = Service("admission_api", runners=[runner])

svc.add_asgi_middleware(JWTAuthMiddleware)
print(">>> Middleware ajouté au service")

# -----------------------------
# LOGIN
# -----------------------------
@svc.api(input=JSON(), output=JSON(), route="/login")
def login(credentials, context):
    print(f">>> LOGIN: credentials reçus = {credentials}")

    username = credentials.get("username")
    password = credentials.get("password")
    print(f">>> LOGIN: username={username}, password={password}")

    if username in USERS and USERS[username] == password:
        print(">>> LOGIN: authentification OK")
        return {"access_token": create_jwt_token(username)}

    print(">>> LOGIN: authentification échouée")
    # Retourner une erreur via la réponse HTTP
    context.response.status_code = 401
    return {"detail": "Invalid username or password"}


# -----------------------------
# PREDICT
# -----------------------------
@svc.api(input=JSON(), output=JSON(), route="/predict")
def predict(input_data, context):
    print(f">>> PREDICT: input_data brut = {input_data}")

    # Parsing Pydantic
    try:
        print(">>> PREDICT: parsing Pydantic…")
        parsed = PredictInput(**input_data)
        print(f">>> PREDICT: parsed = {parsed}")
    except Exception as e:
        print(f">>> PREDICT: erreur Pydantic: {e}")
        context.response.status_code = 400
        return {"detail": "Invalid input"}

    features = [
        parsed.GRE_Score,
        parsed.TOEFL_Score,
        parsed.University_Rating,
        parsed.SOP,
        parsed.LOR,
        parsed.CGPA,
        parsed.Research,
    ]
    print(f">>> PREDICT: features = {features}")

    try:
        print(">>> PREDICT: appel du modèle…")
        # Utiliser le modèle et scaler chargés directement au lieu du runner
        # qui n'est pas initialisé correctement dans les tests
        import numpy as np
        features_array = np.array([features])
        scaled = scaler.transform(features_array)
        print(f">>> PREDICT: scaled = {scaled}")
        pred = model.predict(scaled)
        print(f">>> PREDICT: model output brut = {pred}")
    except Exception as e:
        print(f">>> PREDICT: erreur modèle = {e}")
        context.response.status_code = 500
        return {"detail": "Prediction error"}

    if hasattr(pred, "result"):
        pred = pred.result()
        print(f">>> PREDICT: result() = {pred}")

    if hasattr(pred, "tolist"):
        pred = pred.tolist()
        print(f">>> PREDICT: tolist() = {pred}")

    while isinstance(pred, list):
        pred = pred[0]
        print(f">>> PREDICT: extraction du premier élément = {pred}")

    print(f">>> PREDICT: final = {pred}")
    return {"chance_of_admit": float(pred)}
