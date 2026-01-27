
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
    """Testar att startsidan laddar korrekt (Status 200)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"CM CORP" in response.data

def test_admin_access_denied(client):
    """Testar att man inte kommer in på admin utan inloggning."""
    response = client.get('/admin')
    assert response.status_code == 401 # Unauthorized eller redirect
