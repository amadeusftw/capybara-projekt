"""Repository for Subscriber model - data access layer."""


class SubscriberRepository:
    """Handles data access for Subscriber model."""

    def __init__(self, db):
        """Initialize repository with database instance."""
        self.db = db
        # Import Subscriber from app.app to avoid circular imports
        from app.app import Subscriber
        self.Subscriber = Subscriber

    def get_all(self):
        """
        Retrieve all subscribers ordered by creation date (newest first).
        
        Returns:
            List of Subscriber instances.
        """
        return self.Subscriber.query.order_by(self.Subscriber.created_at.desc()).all()

    def get_by_email(self, email):
        """
        Retrieve a subscriber by email address.
        
        Args:
            email: Subscriber email.
            
        Returns:
            Subscriber instance or None if not found.
        """
        return self.Subscriber.query.filter_by(email=email).first()

    def create(self, first_name, last_name, email, company, title):
        """
        Create and persist a new subscriber.
        
        Args:
            first_name, last_name, email, company, title: Subscriber fields.
            
        Returns:
            Newly created Subscriber instance.
        """
        subscriber = self.Subscriber(
            first_name=first_name,
            last_name=last_name,
            email=email,
            company=company,
            title=title
        )
        self.db.session.add(subscriber)
        self.db.session.commit()
        return subscriber

    def delete(self, subscriber):
        """
        Delete a subscriber.
        
        Args:
            subscriber: Subscriber instance to delete.
        """
        self.db.session.delete(subscriber)
        self.db.session.commit()

    def count(self):
        """Return total number of subscribers."""
        return self.Subscriber.query.count()

