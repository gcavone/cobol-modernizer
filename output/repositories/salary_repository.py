from sqlalchemy.orm import Session
from typing import List
from models.salary_record import SalaryRecord
from repositories.base_repository import BaseRepository


class SalaryRepository(BaseRepository):
    """Repository for managing SalaryRecord entities.
    
    Provides specialized query methods for salary calculations.
    """

    def __init__(self, session: Session) -> None:
        """Initialize SalaryRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, SalaryRecord)

    def get_by_employee_id(self, employee_id: int) -> List[SalaryRecord]:
        """Retrieve all salary records for a specific employee.
        
        Args:
            employee_id: The employee ID.
        
        Returns:
            List of SalaryRecord instances for the given employee.
        """
        return self.session.query(SalaryRecord).filter(
            SalaryRecord.employee_id == employee_id
        ).all()
