import logging
from decimal import Decimal
from typing import List, Optional
from repositories.employee_repository import EmployeeRepository
from repositories.salary_repository import SalaryRepository
from services.activity_service import ActivityService
from models.employee import Employee
from models.salary_record import SalaryRecord


class EmployeeService:
    """Service for managing employees and salary calculations.
    
    Handles employee CRUD operations and salary calculations
    following the rule: SALARY = HOURLY_RATE × HOURS_WORKED
    """

    def __init__(self, employee_repo: EmployeeRepository,
                 salary_repo: SalaryRepository,
                 activity_service: ActivityService) -> None:
        """Initialize EmployeeService with repositories and services.
        
        Args:
            employee_repo: Repository for employee data access.
            salary_repo: Repository for salary record data access.
            activity_service: Service for logging activities.
        """
        self.employee_repo: EmployeeRepository = employee_repo
        self.salary_repo: SalaryRepository = salary_repo
        self.activity_service: ActivityService = activity_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def calculate_salary(self, employee_id: int, hours_worked: float, 
                        admin_id: int) -> SalaryRecord:
        """Calculate and record employee salary.
        
        Implements business rule: SALARY = HOURLY_RATE × HOURS_WORKED
        
        Args:
            employee_id: The employee ID.
            hours_worked: Number of hours worked (must be > 0 and <= 24).
            admin_id: ID of admin performing the calculation.
        
        Returns:
            SalaryRecord with calculated salary.
        
        Raises:
            ValueError: If employee not found or hours invalid.
        """
        # Validate and convert hours_worked
        try:
            hours_decimal: Decimal = Decimal(str(hours_worked))
        except (ValueError, TypeError):
            raise ValueError("Hours worked must be a valid number")

        if hours_decimal <= 0:
            raise ValueError("Hours worked must be positive")

        if hours_decimal > 24:
            raise ValueError("Hours worked cannot exceed 24 per day")

        # Retrieve employee
        employee: Employee = self.get_employee_by_id(employee_id)

        # Calculate salary: SALARY = HOURLY_RATE × HOURS_WORKED
        hourly_rate: Decimal = Decimal(str(employee.hourly_rate))
        total_salary: Decimal = hourly_rate * hours_decimal

        # Create salary record
        salary_record: SalaryRecord = self.salary_repo.create(
            employee_id=employee_id,
            hours_worked=float(hours_decimal),
            hourly_rate=float(hourly_rate),
            total_salary=float(total_salary)
        )

        # Log activity
        self.activity_service.log_action(
            action="SALARY_CALCULATED",
            entity_type="EMPLOYEE",
            entity_id=employee_id,
            admin_id=admin_id,
            details=f"Hours: {hours_decimal}, Rate: {hourly_rate}, Salary: {total_salary}"
        )

        self.logger.info(
            f"Salary calculated for employee {employee_id}: "
            f"{hours_decimal}h × {hourly_rate} = {total_salary}"
        )

        return salary_record

    def get_employee_by_id(self, employee_id: int) -> Employee:
        """Retrieve an employee by ID.
        
        Args:
            employee_id: The employee ID.
        
        Returns:
            Employee instance.
        
        Raises:
            ValueError: If employee not found.
        """
        employee: Optional[Employee] = self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        return employee

    def get_employee_by_employee_id(self, employee_id: str) -> Employee:
        """Retrieve an employee by employee ID code.
        
        Args:
            employee_id: The employee ID code.
        
        Returns:
            Employee instance.
        
        Raises:
            ValueError: If employee not found.
        """
        employee: Optional[Employee] = self.employee_repo.get_by_employee_id(employee_id)
        if not employee:
            raise ValueError(f"Employee ID {employee_id} not found")
        return employee

    def list_all_employees(self) -> List[Employee]:
        """Retrieve all employees sorted by name.
        
        Returns:
            List of all Employee instances.
        """
        return self.employee_repo.get_all_sorted_by_name()

    def create_employee(self, name: str, employee_id: str, 
                       hourly_rate: float = 500.0) -> Employee:
        """Create a new employee.
        
        Args:
            name: Employee full name.
            employee_id: Unique employee ID code.
            hourly_rate: Hourly wage rate (default 500.00).
        
        Returns:
            Created Employee instance.
        
        Raises:
            ValueError: If validation fails or employee_id already exists.
        """
        # Validate name
        if not name or len(name) < 2:
            raise ValueError("Employee name must be at least 2 characters")

        # Validate employee_id
        if not employee_id or len(employee_id) < 2:
            raise ValueError("Employee ID must be at least 2 characters")

        # Check employee_id uniqueness
        if self.employee_repo.get_by_employee_id(employee_id):
            self.logger.warning(f"Employee creation failed: ID already exists - {employee_id}")
            raise ValueError(f"Employee ID {employee_id} already exists")

        # Validate hourly_rate
        try:
            rate_decimal: Decimal = Decimal(str(hourly_rate))
        except (ValueError, TypeError):
            raise ValueError("Hourly rate must be a valid number")

        if rate_decimal <= 0:
            raise ValueError("Hourly rate must be positive")

        # Create employee
        employee: Employee = self.employee_repo.create(
            name=name,
            employee_id=employee_id,
            hourly_rate=float(rate_decimal)
        )

        self.logger.info(f"Employee created: {employee_id} - {name}")

        return employee

    def update_employee(self, employee_id: int, **kwargs) -> Employee:
        """Update an existing employee.
        
        Args:
            employee_id: The employee ID to update.
            **kwargs: Fields to update (name, hourly_rate).
        
        Returns:
            Updated Employee instance.
        
        Raises:
            ValueError: If employee not found or validation fails.
        """
        # Verify employee exists
        employee: Employee = self.get_employee_by_id(employee_id)

        # Validate fields if provided
        if "name" in kwargs:
            name: str = kwargs["name"]
            if not name or len(name) < 2:
                raise ValueError("Employee name must be at least 2 characters")

        if "hourly_rate" in kwargs:
            try:
                rate_decimal: Decimal = Decimal(str(kwargs["hourly_rate"]))
            except (ValueError, TypeError):
                raise ValueError("Hourly rate must be a valid number")
            if rate_decimal <= 0:
                raise ValueError("Hourly rate must be positive")
            kwargs["hourly_rate"] = float(rate_decimal)

        # Update employee
        updated_employee: Optional[Employee] = self.employee_repo.update(
            employee_id, **kwargs
        )

        self.logger.info(f"Employee updated: {employee_id}")

        return updated_employee
