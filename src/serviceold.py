import bentoml
from bentoml.io import JSON
import numpy as np

# Charger le modèle BentoML
model_ref = bentoml.sklearn.get("linear_regression_model:latest")

# Définir un Runnable compatible BentoML 1.4+
class AdmissionRunnable(bentoml.Runnable):
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self):
        self.model = model_ref.to_model()
        self.scaler = self.model.custom_objects["scaler"]

    @bentoml.Runnable.method(batchable=True)
    def predict(self, input_array):
        scaled = self.scaler.transform(input_array)
        return self.model.predict(scaled)

# Créer le Runner
admission_runner = bentoml.Runner(AdmissionRunnable, name="admission_runner")
# Créer le Service 
svc = bentoml.Service("admission_api", runners=[admission_runner])

# Endpoint de prédiction
@svc.api(input=JSON(), output=JSON(), route="/predict")
async def predict(payload):
    features = np.array([[
        payload["GRE Score"],
        payload["TOEFL Score"],
        payload["University Rating"],
        payload["SOP"],
        payload["LOR"],
        payload["CGPA"],
        payload["Research"]
    ]])

    prediction = await admission_runner.predict.async_run(features)
    return {"chance_of_admit": float(prediction[0])}


# Clé secrète JWT (à garder privée)
SECRET_KEY = "SFVfdrfREFE445042dff"

# Login avec JWT

@svc.api(input=JSON(), output=JSON(), route="/login")
def login(payload):
    username = payload.get("username")
    password = payload.get("password")

    # Pour l'examen : validation simple
    if username != "admin" or password != "admin":
        return {"error": "Invalid credentials"}

    # Génération du JWT
    token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return {"access_token": token}


# --------------------------
# 2. Vérification du token
# --------------------------
def verify_token(headers):
    auth = headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth.split(" ")[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None




# Endpoint de prédiction
@svc.api(input=JSON(), output=JSON(), route="/predict")
async def predict(payload):
    features = np.array([[
        payload["GRE Score"],
        payload["TOEFL Score"],
        payload["University Rating"],
        payload["SOP"],
        payload["LOR"],
        payload["CGPA"],
        payload["Research"]
    ]])

    prediction = await admission_runner.predict.async_run(features)
    return {"chance_of_admit": float(prediction[0])}
