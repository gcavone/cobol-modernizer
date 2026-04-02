from sqlalchemy import Column, Integer, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Product(Base):
    """Represents a product in the supermarket inventory.
    
    Attributes:
        id: Unique product identifier (auto-increment).
        code: 8-digit product code (unique).
        name: Product name.
        unit: Unit of measurement (e.g., "155g", "1L").
        price: Unit price in decimal format (must be > 0).
        created_at: Timestamp of product creation.
        updated_at: Timestamp of last product update.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    price = Column(
        Numeric(10, 2),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Return string representation of Product."""
        return (
            f"<Product(id={self.id}, code={self.code}, name={self.name}, "
            f"unit={self.unit}, price={self.price})>"
        )