"""Subscription business logic service."""
from app.data.repositories.subscriber_repository import SubscriberRepository


class SubscriptionService:
    """Handles business logic for subscriptions."""

    def __init__(self, db):
        """
        Initialize service with database instance.
        
        Args:
            db: SQLAlchemy database instance.
        """
        self.repository = SubscriberRepository(db)

    def get_all_subscribers(self):
        """
        Retrieve all subscribers.
        
        Returns:
            List of Subscriber instances ordered by creation date (newest first).
        """
        return self.repository.get_all()

    def get_subscriber_count(self):
        """
        Get the total number of subscribers.
        
        Returns:
            Integer count of subscribers.
        """
        return self.repository.count()

    def register_subscriber(self, first_name, last_name, email, company, title):
        """
        Register a new subscriber.
        
        Args:
            first_name, last_name, email, company, title: Subscriber details.
            
        Returns:
            Created Subscriber instance.
            
        Raises:
            ValueError: If subscriber with email already exists.
        """
        existing = self.repository.get_by_email(email)
        if existing:
            raise ValueError(f"Subscriber with email {email} already exists")
        
        return self.repository.create(first_name, last_name, email, company, title)

    def remove_subscriber(self, email):
        """
        Remove a subscriber by email.
        
        Args:
            email: Email address of subscriber to remove.
            
        Raises:
            ValueError: If subscriber not found.
        """
        subscriber = self.repository.get_by_email(email)
        if not subscriber:
            raise ValueError(f"Subscriber with email {email} not found")
        
        self.repository.delete(subscriber)
