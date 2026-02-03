# Använd en Python-miljö
FROM python:3.9-slim

# Sätt arbetskatalogen
WORKDIR /code

# Kopiera allt till containern
COPY . .

# Installera beroenden (Flask, etc)
RUN pip install --no-cache-dir -r requirements.txt

# Öppna port 5000
EXPOSE 5000

# Berätta var appen finns och att den ska lyssna på alla IP-adresser
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Starta appen
CMD ["flask", "run", "--port=5000"]
