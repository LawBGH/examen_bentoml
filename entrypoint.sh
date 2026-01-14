#!/bin/bash

# Entraîner les modèles si nécessaire
cd /app
python3 src/train_model.py

# Lancer le service BentoML
bentoml serve src.service:svc --production
