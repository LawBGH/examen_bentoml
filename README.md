# API de Prédiction d'Admission - BentoML



## Table des matières
- [Prérequis](#prérequis)
- [Installation et démarrage](#installation-et-démarrage)
- [Tests unitaires](#tests-unitaires)
- [Endpoints API](#endpoints-api)
- [Architecture](#architecture)

---

## Prérequis

- Docker installé et configuré
- Python 3.11+ (pour tests locaux)
- curl ou Postman (pour tester les endpoints)
- 8 GB de RAM minimum

---

## Installation et démarrage

### Option 1 : Utiliser l'image Docker 

#### Étape 1 : Charger l'image Docker
```bash
# Depuis le répertoire racine du projet
docker load -i admission_api.tar.gz
```

#### Étape 2 : Lancer le conteneur
```bash
docker run -d -p 3000:3000 --name admission_api admission_api:latest
```

Le service démarre automatiquement sur `http://localhost:3000`


#### Étape 3 : Vérifier que le service fonctionne
```bash
curl http://localhost:3000
```



---

## Tests unitaires

### Tests locaux (avec venv)

#### Étape 1 : Activer l'environnement virtuel
```bash
cd examen_bentoml
source venv311/bin/activate
```

#### Étape 2 : Lancer tous les tests
```bash
pytest -v
```

**Résultat attendu :**
```
======================== 9 passed in 11.18s ========================
```

Tous les tests retournent le statut **PASSED** ✅

#### Tests spécifiques :
```bash
# Tests d'authentification (3 tests)
pytest tests/test_authent.py -v

# Tests de login et prédiction (2 tests)
pytest tests/test_login_predict.py -v

# Tests de prédiction (4 tests)
pytest tests/test_predict.py -v
```

### Tests via API HTTP

#### Étape 1 : Obtenir un JWT token
```bash
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "LawrenceBENE", "password": "BentoMlTop"}'
```

**Réponse :**
```json
{"access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}
```

#### Étape 2 : Utiliser le token pour faire une prédiction
```bash
TOKEN="votre_token_ici"
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "GRE Score": 330,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.5,
    "CGPA": 3.54,
    "Research": 1
  }'
```

**Réponse :**
```json
{"chance_of_admit": 0.22984405833562904}
```

---

## Endpoints API

### 1. POST `/login`
Authentification utilisateur et obtention du JWT token.

**Requête :**
```json
{
  "username": "LawrenceBENE",
  "password": "BentoMlTop"
}
```

**Réponse (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Erreurs :**
- `400` : Identifiants invalides
- `422` : Données manquantes

---

### 2. POST `/predict`
Prédire la probabilité d'admission (nécessite un JWT token valide).

**Headers requis :**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Requête :**
```json
{
  "GRE Score": 330,
  "TOEFL Score": 110,
  "University Rating": 4,
  "SOP": 4.5,
  "LOR": 4.5,
  "CGPA": 3.54,
  "Research": 1
}
```

**Paramètres :**
| Champ | Type | Range | Description |
|-------|------|-------|-------------|
| GRE Score | float | 260-340 | Score Graduate Record Exam |
| TOEFL Score | float | 0-120 | Score Test of English as Foreign Language |
| University Rating | int | 1-5 | Classement de l'université |
| SOP | float | 0-5 | Statement of Purpose (1-5) |
| LOR | float | 0-5 | Letter of Recommendation (1-5) |
| CGPA | float | 0-4 | Note générale cumulative |
| Research | int | 0-1 | Expérience recherche (0=Non, 1=Oui) |

**Réponse (200):**
```json
{
  "chance_of_admit": 0.72
}
```

**Erreurs :**
- `400` : Données invalides
- `401` : Token manquant ou invalide
- `422` : Champs requis manquants

---

### 3. GET `/metrics`
Métriques Prometheus du service.

---

## Architecture

### Structure du projet
```
examen_bentoml/
├── src/
│   ├── service.py           # Service BentoML avec endpoints
│   ├── train_model.py       # Entraînement du modèle ML
│   ├── prepare_data.py      # Préparation des données
│   └── config.py            # Configuration
├── tests/
│   ├── test_authent.py      # Tests authentification
│   ├── test_login_predict.py # Tests login/predict
│   └── test_predict.py      # Tests prédiction
├── data/
│   ├── raw/
│   │   └── admission.csv    # Données brutes
│   └── processed/
│       ├── x_train.csv
│       ├── x_test.csv
│       ├── y_train.csv
│       └── y_test.csv
├── models/
│   └── metrics/
│       └── metrics.txt      # Évaluation du modèle
├── Dockerfile               # Configuration Docker
├── entrypoint.sh            # Script démarrage conteneur
├── requirements.txt         # Dépendances Python
├── bentofile.yaml          # Configuration BentoML
└── conftest.py             # Configuration pytest
```

### Modèle ML
- **Algorithme :** Linear Regression (scikit-learn)
- **Features :** 7 variables prédictives
- **Performance :** R² = 0.8188, MSE = 0.0037
- **Target :** Probabilité d'admission (0-1)

### Stack technique
- **Framework :** BentoML 1.1.10
- **API HTTP :** Starlette
- **ML :** scikit-learn
- **Authentification :** JWT
- **Conteneurisation :** Docker
- **Tests :** pytest

---

## Gestion du conteneur

### Afficher les logs
```bash
docker logs admission_api
```

### Arrêter le service
```bash
docker stop admission_api
```

### Redémarrer le service
```bash
docker restart admission_api
```

### Supprimer le conteneur
```bash
docker rm admission_api
```

### Supprimer l'image
```bash
docker rmi admission_api:latest
```

---

## Troubleshooting

### Le service ne répond pas
```bash
# Vérifier l'état du conteneur
docker ps | grep admission_api

# Vérifier les logs d'erreur
docker logs admission_api | tail -50
```

### Erreur "Connection refused"
- Vérifier que le conteneur est en cours d'exécution : `docker ps`
- Attendre 10-15 secondes le démarrage complet
- Vérifier le port 3000 : `netstat -tlnp | grep 3000`

### Tests échouent
```bash
# Réinitialiser l'environnement
source venv311/bin/activate
pytest --tb=short -v
```

---

## Informations additionnelles

- **API URL :** http://localhost:3000
- **Métriques :** http://localhost:3000/metrics
