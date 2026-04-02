from sqlalchemy import Column, Integer, Numeric, DateTime, CheckConstraint
from models.product import Base
from datetime import datetime


class ProfitRecord(Base):
    """Represents a profit calculation record.
    
    Attributes:
        id: Unique profit record identifier (auto-increment).
        cogs: Cost of goods sold (must be >= 0).
        selling_price: Selling price (must be > 0).
        profit: Calculated profit (selling_price - cogs).
        created_at: Timestamp of profit calculation.
    """

    __tablename__ = "profit_records"

    id = Column(Integer, primary_key=True)
    cogs = Column(
        Numeric(10, 2),
        nullable=False,
    )
    selling_price = Column(
        Numeric(10, 2),
        nullable=False,
    )
    profit = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Return string representation of ProfitRecord."""
        return (
            f"<ProfitRecord(id={self.id}, cogs={self.cogs}, "
            f"selling_price={self.selling_price}, profit={self.profit}, "
            f"created_at={self.created_at})>"
        )