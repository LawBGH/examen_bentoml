import os
import sys

# === Avant toute importation de bentoml, empecher le chargement de prometheus_client ===
os.environ["BENTOML_DISABLE_METRICS"] = "true"
os.environ["PROMETHEUS_MULTIPROC_DIR"] = ""

# Empêcher prometheus_client de se charger en multiprocessing sinon erreurs de duplicate
if "prometheus_client" in sys.modules:
    del sys.modules["prometheus_client"]

import pytest
from starlette.testclient import TestClient

def pytest_configure(config):
    # Ajouter la racine du projet au PYTHONPATH
    ROOT = os.path.dirname(os.path.abspath(__file__))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

@pytest.fixture(scope="session")
def client():
    """Créer un client de test pour toute la session de tests"""
    from src.service import svc
    return TestClient(svc.asgi_app)
