from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, CheckConstraint
from models.product import Base
from datetime import datetime


class SalaryRecord(Base):
    """Represents a salary calculation record for an employee.
    
    Attributes:
        id: Unique salary record identifier (auto-increment).
        employee_id: Foreign key reference to the employee.
        hours_worked: Number of hours worked (must be > 0).
        hourly_rate: Hourly rate applied for this calculation.
        total_salary: Calculated total salary (hourly_rate × hours_worked).
        created_at: Timestamp of salary calculation.
    """

    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    hours_worked = Column(
        Numeric(5, 2),
        nullable=False,
    )
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    total_salary = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Return string representation of SalaryRecord."""
        return (
            f"<SalaryRecord(id={self.id}, employee_id={self.employee_id}, "
            f"hours_worked={self.hours_worked}, hourly_rate={self.hourly_rate}, "
            f"total_salary={self.total_salary}, created_at={self.created_at})>"
        )