from sqlalchemy.orm import Session
from models.profit_record import ProfitRecord
from repositories.base_repository import BaseRepository


class ProfitRepository(BaseRepository):
    """Repository for managing ProfitRecord entities.
    
    Provides CRUD operations for profit calculations.
    """

    def __init__(self, session: Session) -> None:
        """Initialize ProfitRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, ProfitRecord)
