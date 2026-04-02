from sqlalchemy import Column, Integer, String, Numeric, DateTime
from models.product import Base
from datetime import datetime


class Order(Base):
    """Represents a customer order transaction.
    
    Attributes:
        id: Unique order identifier (auto-increment).
        order_number: Unique order receipt number.
        total_amount: Total order amount in decimal format.
        payment_amount: Amount paid by customer in decimal format.
        change_amount: Change returned to customer (PAYMENT - TOTAL).
        created_at: Timestamp of order creation.
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_amount = Column(Numeric(10, 2), nullable=False)
    change_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Return string representation of Order."""
        return (
            f"<Order(id={self.id}, order_number={self.order_number}, "
            f"total_amount={self.total_amount}, payment_amount={self.payment_amount}, "
            f"change_amount={self.change_amount}, created_at={self.created_at})>"
        )