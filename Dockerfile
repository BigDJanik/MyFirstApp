# Verwenden eines Basis Images
FROM python:3.10

# Definition des Arbeitsverzeichnisses
WORKDIR /app

# Kopieren des Codes
COPY . /app

# Installieren der Abhängigkeiten
RUN pip install -r requirements.txt

# Verfügbarkeit des Ports
EXPOSE 8501

# App starten
CMD ["streamlit", "run", "app.py"]

