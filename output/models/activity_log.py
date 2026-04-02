from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.product import Base
from datetime import datetime


class ActivityLog(Base):
    """Represents a log entry for system activities and administrative actions.
    
    Attributes:
        id: Unique activity log identifier (auto-increment).
        action: Type of action performed (e.g., CREATE, UPDATE, DELETE, LOGIN).
        entity_type: Type of entity affected (e.g., PRODUCT, ORDER, EMPLOYEE).
        entity_id: ID of the entity affected (nullable for some actions).
        admin_id: Foreign key reference to the admin who performed the action.
        details: Additional details about the action (nullable).
        created_at: Timestamp of the activity.
    """

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Return string representation of ActivityLog."""
        return (
            f"<ActivityLog(id={self.id}, action={self.action}, "
            f"entity_type={self.entity_type}, entity_id={self.entity_id}, "
            f"admin_id={self.admin_id}, created_at={self.created_at})>"
        )