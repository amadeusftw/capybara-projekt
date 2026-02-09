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

# Copy and set up entrypoint script
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# Run entrypoint script which handles DB init and admin seeding
ENTRYPOINT ["/code/entrypoint.sh"]
