# src/service.py
import bentoml
from bentoml.legacy import Service, Runnable, Runner
from bentoml.io import JSON
import numpy as np

# charger modèles
model = bentoml.sklearn.load_model("linear_regression_model:latest")
# On applique le même scaler que celui utilisé lors de l'entraînement, et on va
# l'utiliser pour transformer les données d'entrée avant de faire chaque prédiction
scaler = bentoml.sklearn.load_model("data_scaler:latest")


# Runnable legacy
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

# Runner legacy
admission_runner = Runner(AdmissionRunnable, name="admission_runner")

# Service legacy
svc = Service("admission_api", runners=[admission_runner])

@svc.api(input=JSON(), output=JSON(), route="/predict")
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

    # Normalisation du format de sortie
    value = prediction
    if hasattr(value, "tolist"):
        value = value.tolist()

    while isinstance(value, list):
        value = value[0]

    return {"chance_of_admit": float(value)}

