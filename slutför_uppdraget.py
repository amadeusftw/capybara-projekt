import os

print("### ANALYSERAR OCH KOMPLETTERAR ENLIGT KRAVSPECIFIKATIONER... ###")

# --- 1. SÄKERSTÄLL REQUIREMENTS (KRAV: AZURE & TESTER) ---
req_file = "requirements.txt"
required_packages = ["pytest", "gunicorn"] 

try:
    with open(req_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    with open(req_file, "a", encoding="utf-8") as f:
        for package in required_packages:
            if package not in content:
                f.write(f"\n{package}")
                print(f"✅ [KRAV] Lade till '{package}' i requirements.txt")
            else:
                print(f"ℹ️  '{package}' fanns redan.")
except FileNotFoundError:
    print("⚠️  requirements.txt saknades. Skapar ny.")
    with open(req_file, "w", encoding="utf-8") as f:
        f.write("Flask==3.0.0\nFlask-SQLAlchemy==3.1.1\nFlask-WTF==1.2.1\nFlask-Login==0.6.3\nemail_validator\ngunicorn\npytest")

# --- 2. SKAPA PROCFILE (KRAV: HOSTING PÅ AZURE) ---
procfile_content = "web: gunicorn app.app:app"
with open("Procfile", "w", encoding="utf-8") as f:
    f.write(procfile_content)
print("✅ [KRAV] Skapade 'Procfile' för Azure-hosting.")

# --- 3. SKAPA ENHETSTESTER (KRAV: PROJECT STRUCTURE PDF) ---
os.makedirs("tests", exist_ok=True)
test_code = """
import pytest
from app.app import app, db, Subscriber

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_home_page_loads(client):
    \"\"\"Testar att startsidan laddar korrekt (Status 200).\"\"\"
    response = client.get('/')
    assert response.status_code == 200
    assert b"CM CORP" in response.data

def test_admin_access_denied(client):
    \"\"\"Testar att man inte kommer in på admin utan inloggning.\"\"\"
    response = client.get('/admin')
    assert response.status_code == 401 # Unauthorized eller redirect
"""
with open("tests/test_app.py", "w", encoding="utf-8") as f:
    f.write(test_code)
print("✅ [KRAV] Skapade enhetstester i 'tests/test_app.py'.")

# --- 4. SKAPA GITHUB ACTIONS PIPELINE (KRAV: CI/CD) ---
os.makedirs(".github/workflows", exist_ok=True)
workflow_code = """name: CM Corp CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: "3.10"
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run Tests (Pytest)
      run: |
        export PYTHONPATH=$PYTHONPATH:.
        pytest
"""
with open(".github/workflows/main_pipeline.yml", "w", encoding="utf-8") as f:
    f.write(workflow_code)
print("✅ [KRAV] Skapade CI/CD-pipeline i '.github/workflows/main_pipeline.yml'.")

print("\n### 🚀 ALLA UPPDRAG SLUTFÖRDA! ###")