# src/service.py

import bentoml
# Importe la bibliothèque BentoML, utilisée pour charger les modèles et créer le service.

from bentoml.legacy import Service, Runnable, Runner
# Importe les classes de l’API legacy : Service pour définir l’API, Runnable pour encapsuler la logique,
# Runner pour exécuter le runnable de manière optimisée.

from bentoml.io import JSON
# Importe le type d’entrée/sortie JSON pour définir les formats des endpoints.

import numpy as np
# Importe NumPy pour manipuler les tableaux numériques.


# charger modèles
model = bentoml.sklearn.load_model("linear_regression_model:latest")
# Charge le modèle de régression linéaire depuis le Model Store BentoML.

# On applique le même scaler que celui utilisé lors de l'entraînement, et on va
# l'utiliser pour transformer les données d'entrée avant de faire chaque prédiction
scaler = bentoml.sklearn.load_model("data_scaler:latest")
# Charge le scaler utilisé pendant l’entraînement pour normaliser les données entrantes.


# Runnable legacy
class AdmissionRunnable(Runnable):
    # Déclare une classe Runnable, qui encapsule la logique de prédiction.

    SUPPORTED_RESOURCES = ("cpu",)
    # Indique que ce runnable peut s’exécuter sur CPU.

    SUPPORTS_CPU_MULTI_THREADING = True
    # Indique que le runnable supporte le multithreading CPU.

    def __init__(self):
        # Constructeur du runnable.
        self.model = model
        # Stocke le modèle chargé.
        self.scaler = scaler
        # Stocke le scaler chargé.

    @Runnable.method(batchable=True)
    # Déclare une méthode exécutable par le Runner. batchable=True permet de traiter plusieurs entrées à la fois.
    def predict(self, arr):
        # Fonction de prédiction appelée par le runner.
        scaled = self.scaler.transform(arr)
        # Applique le scaler aux données d’entrée.
        return self.model.predict(scaled)
        # Retourne la prédiction du modèle sur les données transformées.


# Runner
admission_runner = Runner(AdmissionRunnable, name="admission_runner")
# Crée un Runner basé sur le runnable, permettant une exécution optimisée et parallèle.


# Service
svc = Service("admission_api", runners=[admission_runner])
# Déclare un service BentoML nommé "admission_api" et lui associe le runner.


@svc.api(input=JSON(), output=JSON(), route="/predict")
# Déclare un endpoint HTTP POST /predict, acceptant du JSON en entrée et renvoyant du JSON en sortie.
def predict(payload):
    # Fonction exécutée lorsqu’un POST est envoyé sur /predict.

    features = np.array([[
        payload["GRE Score"],
        payload["TOEFL Score"],
        payload["University Rating"],
        payload["SOP"],
        payload["LOR"],
        payload["CGPA"],
        payload["Research"]
    ]])
    # Construit un tableau NumPy 2D contenant les 7 features attendues par le modèle.
    # Les clés doivent correspondre exactement à celles du JSON reçu.

    prediction = admission_runner.predict.run(features)
    # Appelle la méthode predict du runner pour obtenir la prédiction.

    # Normalisation du format de sortie
    value = prediction
    # Stocke la prédiction dans une variable intermédiaire.

    if hasattr(value, "tolist"):
        value = value.tolist()
    # Convertit un éventuel tableau NumPy ou NdarrayContainer en liste Python.

    while isinstance(value, list):
        value = value[0]
    # Aplati la structure si elle est imbriquée (par exemple [[0.82]] → 0.82).

    return {"chance_of_admit": float(value)}
    # Retourne la prédiction sous forme de float dans un dictionnaire JSON.
