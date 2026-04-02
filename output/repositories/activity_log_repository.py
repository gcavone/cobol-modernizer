from sqlalchemy.orm import Session
from typing import List
from models.activity_log import ActivityLog
from repositories.base_repository import BaseRepository


class ActivityLogRepository(BaseRepository):
    """Repository for managing ActivityLog entities.
    
    Provides specialized query methods for activity logs.
    """

    def __init__(self, session: Session) -> None:
        """Initialize ActivityLogRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, ActivityLog)

    def get_by_admin_id(self, admin_id: int) -> List[ActivityLog]:
        """Retrieve all activity logs for a specific admin.
        
        Args:
            admin_id: The admin ID.
        
        Returns:
            List of ActivityLog instances for the given admin.
        """
        return self.session.query(ActivityLog).filter(
            ActivityLog.admin_id == admin_id
        ).all()
