from sqlalchemy.orm import Session
from typing import List
from models.order_item import OrderItem
from repositories.base_repository import BaseRepository


class OrderItemRepository(BaseRepository):
    """Repository for managing OrderItem entities.
    
    Provides specialized query methods for order line items.
    """

    def __init__(self, session: Session) -> None:
        """Initialize OrderItemRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, OrderItem)

    def get_by_order_id(self, order_id: int) -> List[OrderItem]:
        """Retrieve all items for a specific order.
        
        Args:
            order_id: The order ID.
        
        Returns:
            List of OrderItem instances for the given order.
        """
        return self.session.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).all()
