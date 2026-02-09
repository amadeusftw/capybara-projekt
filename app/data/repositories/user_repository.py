"""Repository for User model - data access layer."""


class UserRepository:
    """Handles data access for User model."""

    def __init__(self, db):
        """Initialize repository with database instance."""
        self.db = db
        # Import User from app.app to avoid circular imports
        from app.app import User
        self.User = User

    def get_by_username(self, username):
        """
        Retrieve a user by username.
        
        Args:
            username: Username to search for.
            
        Returns:
            User instance or None if not found.
        """
        return self.User.query.filter_by(username=username).first()

    def get_by_id(self, user_id):
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User ID.
            
        Returns:
            User instance or None if not found.
        """
        return self.db.session.get(self.User, user_id)

    def create(self, username, password_hash):
        """
        Create and persist a new user.
        
        Args:
            username: Unique username.
            password_hash: Pre-hashed password.
            
        Returns:
            Newly created User instance.
        """
        user = self.User(username=username, password_hash=password_hash)
        self.db.session.add(user)
        self.db.session.commit()
        return user

    def delete(self, user):
        """
        Delete a user.
        
        Args:
            user: User instance to delete.
        """
        self.db.session.delete(user)
        self.db.session.commit()

