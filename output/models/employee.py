from sqlalchemy import Column, Integer, String, Numeric, DateTime
from models.product import Base
from datetime import datetime


class Employee(Base):
    """Represents an employee in the supermarket.
    
    Attributes:
        id: Unique employee identifier (auto-increment).
        name: Employee full name.
        employee_id: Unique employee ID code.
        hourly_rate: Hourly wage rate in decimal format (default 500.00).
        created_at: Timestamp of employee record creation.
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    employee_id = Column(String(20), unique=True, nullable=False)
    hourly_rate = Column(Numeric(10, 2), nullable=False, default=500.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Return string representation of Employee."""
        return (
            f"<Employee(id={self.id}, name={self.name}, "
            f"employee_id={self.employee_id}, hourly_rate={self.hourly_rate})>"
        )