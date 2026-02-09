"""User model for admin authentication with Flask-Login support."""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    """Admin user model with password authentication."""
    __tablename__ = 'user'
    
    id = None  # Will be set by db.Column in app.py
    username = None
    password_hash = None
    is_active = None

    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

