from sqlalchemy.orm import Session
from typing import Optional
from models.admin import Admin
from repositories.base_repository import BaseRepository


class AdminRepository(BaseRepository):
    """Repository for managing Admin entities.
    
    Provides specialized query methods for admin users.
    """

    def __init__(self, session: Session) -> None:
        """Initialize AdminRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, Admin)

    def get_by_email(self, email: str) -> Optional[Admin]:
        """Retrieve an admin by email address.
        
        Args:
            email: The admin email address.
        
        Returns:
            The Admin instance if found, None otherwise.
        """
        return self.session.query(Admin).filter(
            Admin.email == email
        ).first()
