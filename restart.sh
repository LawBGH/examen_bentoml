#!/bin/bash

echo "=== RESET COMPLET BENTOML ==="

echo "→ Arrêt des serveurs BentoML en cours..."
pkill -f bentoml 2>/dev/null

echo "→ Arrêt des workers Circus..."
pkill -f circus 2>/dev/null

echo "→ Libération des ports 3000 et 3001..."
for PORT in 3000 3001; do
    PID=$(lsof -t -i:$PORT)
    if [ ! -z "$PID" ]; then
        echo "  - Port $PORT occupé par PID $PID → kill"
        kill -9 $PID
    else
        echo "  - Port $PORT libre"
    fi
done

echo "→ Pause 1 seconde..."
sleep 1

echo "→ Lancement du service BentoML sur le port 3000..."
bentoml serve --reload --port 3000 src/service.py:svc
