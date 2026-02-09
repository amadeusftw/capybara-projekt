"""Authentication business logic service."""
from sqlalchemy.exc import IntegrityError
from app.data.repositories.user_repository import UserRepository
from app.data.models.user import User


class DuplicateUsernameError(Exception):
    """Raised when attempting to create user with existing username."""
    pass


class AuthService:
    """Handles authentication and user management logic."""

    def __init__(self, db):
        """
        Initialize service with database instance.
        
        Args:
            db: SQLAlchemy database instance.
        """
        self.repository = UserRepository(db)
        self.db = db

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate user by username and password.
        
        Args:
            username: User's username.
            password: User's password (plain text).
            
        Returns:
            User instance if credentials are valid and user is active, None otherwise.
        """
        from app.app import db
        repository = UserRepository(db)
        user = repository.get_by_username(username)
        
        if user and user.is_active and user.check_password(password):
            return user
        return None

    @staticmethod
    def create_user(username, password):
        """
        Create a new user with hashed password.
        
        Args:
            username: Unique username.
            password: Plain text password (will be hashed).
            
        Returns:
            Created User instance.
            
        Raises:
            DuplicateUsernameError: If username already exists.
        """
        from app.app import db
        repository = UserRepository(db)
        
        user = User(username=username)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise DuplicateUsernameError(f"Username '{username}' already exists")

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve user by ID.
        
        Args:
            user_id: User ID.
            
        Returns:
            User instance or None if not found.
        """
        from app.app import db
        repository = UserRepository(db)
        return repository.get_by_id(user_id)
