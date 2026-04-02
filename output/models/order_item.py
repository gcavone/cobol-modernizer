from sqlalchemy import Column, Integer, Numeric, ForeignKey, CheckConstraint
from models.product import Base


class OrderItem(Base):
    """Represents a line item in a customer order.
    
    Attributes:
        id: Unique order item identifier (auto-increment).
        order_id: Foreign key reference to the parent order.
        product_id: Foreign key reference to the product.
        quantity: Number of units ordered (must be > 0).
        unit_price: Price per unit at time of order.
        subtotal: Total for this line item (quantity × unit_price).
    """

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(
        Integer,
        nullable=False,
        default=1,
    )
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    def __repr__(self) -> str:
        """Return string representation of OrderItem."""
        return (
            f"<OrderItem(id={self.id}, order_id={self.order_id}, "
            f"product_id={self.product_id}, quantity={self.quantity}, "
            f"unit_price={self.unit_price}, subtotal={self.subtotal})>"
        )