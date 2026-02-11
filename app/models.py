from datetime import datetime
from flask_login import UserMixin
from app.extensions import db

# --- HÄR DEFINIERAR VI DATABAS-STRUKTUREN ---

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    company = db.Column(db.String(100))
    title = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin):
    def __init__(self, id, is_admin=True):
        self.id = id
        self.is_admin = is_admin