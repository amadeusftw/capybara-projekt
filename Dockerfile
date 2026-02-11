FROM python:3.9-slim
WORKDIR /code

# Copy everything first
COPY . .

# Verify templates copied (Bra debugging-steg!)
RUN ls -la app/templates/ && echo "Templates copied successfully"

RUN pip install --no-cache-dir -r requirements.txt

# Set Python path
ENV PYTHONPATH=/code
ENV FLASK_ENV=production

# Vi kör på standardport 8000 för Gunicorn
EXPOSE 8000

# Copy and set up entrypoint script
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# Starta scriptet
ENTRYPOINT ["/code/entrypoint.sh"]