FROM python:3.9-slim
WORKDIR /code

# Copy everything first
COPY . .

# Verify templates copied
RUN ls -la app/templates/ && echo "Templates copied successfully"

RUN pip install --no-cache-dir -r requirements.txt

# Set Python path
ENV PYTHONPATH=/code
ENV FLASK_ENV=production

EXPOSE 5000

# Run gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
