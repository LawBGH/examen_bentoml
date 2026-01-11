#!/bin/bash
# Suppose que bento serve fonctionne
# bentoml serve
#
bentoml serve src.service:svc --port 3001

sleep 5  # Attendre que le serveur démarre


echo "=== LOGIN ==="
TOKEN=$(curl -s -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"LawrenceBENE","password":"BentoMlTop"}' | jq -r '.token')

echo "Token reçu : $TOKEN"

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "Erreur : impossible d'obtenir un token"
  exit 1
fi

echo "=== PREDICT ==="
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.0,
    "CGPA": 9.2,
    "Research": 1
  }'
