from sqlalchemy.orm import Session
from typing import Optional, List
from models.order import Order
from repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    """Repository for managing Order entities.
    
    Provides specialized query methods for customer orders.
    """

    def __init__(self, session: Session) -> None:
        """Initialize OrderRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, Order)

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """Retrieve an order by its order number.
        
        Args:
            order_number: The unique order number.
        
        Returns:
            The Order instance if found, None otherwise.
        """
        return self.session.query(Order).filter(
            Order.order_number == order_number
        ).first()

    def get_all_sorted_by_date(self) -> List[Order]:
        """Retrieve all orders sorted by creation date (newest first).
        
        Returns:
            List of all Order instances ordered by created_at descending.
        """
        return self.session.query(Order).order_by(
            Order.created_at.desc()
        ).all()
