FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/
COPY bentofile.yaml .
COPY data/ ./data/
COPY entrypoint.sh .

# Donner les permissions d'exécution au script
RUN chmod +x /app/entrypoint.sh

# Exposer le port par défaut de BentoML
EXPOSE 3000

# Utiliser le script d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
