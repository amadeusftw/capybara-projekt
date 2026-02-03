FROM python:3.9-slim
WORKDIR /code
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Viktigt: Sätt PYTHONPATH så den hittar mappen 'app'
ENV PYTHONPATH=/code
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

# Vi kör flask direkt. Detta skapar db via din 'with app.app_context()' i app.py
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
