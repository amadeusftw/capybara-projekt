"""Authentication business logic service."""
from sqlalchemy.exc import IntegrityError


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
        from app.app import app, User
        
        # Ensure we're in the app context
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            
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
        from app.app import app, db, User
        
        # Ensure we're in the app context
        with app.app_context():
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
        from app.app import app, User
        
        # Ensure we're in the app context
        with app.app_context():
            return User.query.get(user_id)
