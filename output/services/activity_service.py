import logging
from datetime import datetime
from repositories.activity_log_repository import ActivityLogRepository
from models.activity_log import ActivityLog


class ActivityService:
    """Service for logging system activities and administrative actions.
    
    Records all significant actions in both database and log file
    for audit trail and debugging purposes.
    """

    def __init__(self, activity_repo: ActivityLogRepository) -> None:
        """Initialize ActivityService with activity log repository.
        
        Args:
            activity_repo: Repository for activity log data access.
        """
        self.activity_repo: ActivityLogRepository = activity_repo
        self.logger: logging.Logger = logging.getLogger(__name__)

    def log_action(self, action: str, entity_type: str, entity_id: int | None = None,
                   admin_id: int | None = None, details: str | None = None) -> ActivityLog:
        """Log an activity to database and file.
        
        Records administrative actions and system events for audit trail.
        
        Args:
            action: Type of action (e.g., CREATE, UPDATE, DELETE, LOGIN).
            entity_type: Type of entity affected (e.g., PRODUCT, ORDER, EMPLOYEE).
            entity_id: ID of the entity affected (optional).
            admin_id: ID of admin who performed the action (optional).
            details: Additional details about the action (optional).
        
        Returns:
            ActivityLog instance.
        """
        # Validate action and entity_type
        if not action or len(action) < 1:
            raise ValueError("Action is required")

        if not entity_type or len(entity_type) < 1:
            raise ValueError("Entity type is required")

        # Create activity log record
        activity_log: ActivityLog = self.activity_repo.create(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            admin_id=admin_id,
            details=details
        )

        # Log to file
        log_message: str = (
            f"Action: {action} | Entity: {entity_type}:{entity_id} | "
            f"Admin: {admin_id} | Details: {details}"
        )
        self.logger.info(log_message)

        return activity_log
