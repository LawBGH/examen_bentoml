#!/bin/bash
#touch src/__init__.py
#source venv/bin/activate
python3 -c "import src.service; print('OK')"
#bentoml serve src/service.py
nohup bentoml serve src/service.py --host 0.0.0.0 --port 3000 > bentoml.log 2>&1 &
sleep 15

curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.0,
    "CGPA": 9.2,
    "Research": 1
  }'

# desactive le service bentoML
sudo lsof -i :3000 | awk 'NR>1 {print $2}' | xargs sudo kill -9
