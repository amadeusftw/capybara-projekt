FROM python:3.9-slim
WORKDIR /code
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Viktigt: Sätt PYTHONPATH så den hittar mappen 'app'
ENV PYTHONPATH=/code
ENV FLASK_ENV=production

EXPOSE 5000

# Kör gunicorn för production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
