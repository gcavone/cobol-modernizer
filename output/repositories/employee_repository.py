from sqlalchemy.orm import Session
from typing import Optional, List
from models.employee import Employee
from repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository):
    """Repository for managing Employee entities.
    
    Provides specialized query methods for employees.
    """

    def __init__(self, session: Session) -> None:
        """Initialize EmployeeRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, Employee)

    def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Retrieve an employee by their employee ID code.
        
        Args:
            employee_id: The unique employee ID code.
        
        Returns:
            The Employee instance if found, None otherwise.
        """
        return self.session.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()

    def get_all_sorted_by_name(self) -> List[Employee]:
        """Retrieve all employees sorted alphabetically by name.
        
        Returns:
            List of all Employee instances ordered by name.
        """
        return self.session.query(Employee).order_by(Employee.name).all()
