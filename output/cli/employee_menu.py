import logging
from typing import List
from services.employee_service import EmployeeService
from cli.ui_helpers import clear_screen, print_header, ask_continue, print_table, format_currency


class EmployeeMenu:
    """Employee management menu for administrators.
    
    Provides employee CRUD and salary calculation operations.
    """

    def __init__(self, employee_service: EmployeeService, admin_id: int) -> None:
        """Initialize EmployeeMenu with required services.
        
        Args:
            employee_service: Service for employee management.
            admin_id: ID of logged-in administrator.
        """
        self.employee_service: EmployeeService = employee_service
        self.admin_id: int = admin_id
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display employee menu and handle selections.
        
        Loops until user chooses to exit.
        """
        while True:
            clear_screen()
            print_header("EMPLOYEE MANAGEMENT")

            print("\n1) List Employees")
            print("2) Add Employee")
            print("3) Calculate Salary")
            print("4) Back to Admin Menu")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                self.list_employees()
            elif choice == "2":
                self.add_employee()
            elif choice == "3":
                self.calculate_salary()
            elif choice == "4":
                break
            else:
                print("\n❌ Invalid choice. Please select 1-4.")
                input("Press Enter to continue...")

    def list_employees(self) -> None:
        """Display all employees in a formatted table."""
        clear_screen()
        print_header("EMPLOYEE LIST")

        try:
            employees = self.employee_service.list_all_employees()

            if not employees:
                print("\nNo employees found.")
                input("Press Enter to continue...")
                return

            headers: List[str] = ["ID", "Name", "Employee ID", "Hourly Rate"]
            rows: List[List[str]] = [
                [
                    str(e.id),
                    e.name,
                    e.employee_id,
                    format_currency(float(e.hourly_rate))
                ]
                for e in employees
            ]

            print()
            print_table(headers, rows)
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\n❌ Error loading employees: {str(e)}")
            self.logger.error(f"Error in list_employees: {str(e)}")
            input("Press Enter to continue...")

    def add_employee(self) -> None:
        """Add a new employee."""
        clear_screen()
        print_header("ADD NEW EMPLOYEE")

        try:
            name: str = input("\nEmployee Name: ").strip()
            employee_id: str = input("Employee ID: ").strip()

            hourly_rate_input: str = input("Hourly Rate (default 500.00): ").strip()
            hourly_rate: float = 500.0

            if hourly_rate_input:
                try:
                    hourly_rate = float(hourly_rate_input)
                except ValueError:
                    print("❌ Invalid hourly rate format")
                    input("Press Enter to continue...")
                    return

            employee = self.employee_service.create_employee(
                name=name,
                employee_id=employee_id,
                hourly_rate=hourly_rate
            )

            print(f"\n✓ Employee created successfully!")
            print(f"  Name: {employee.name}")
            print(f"  Employee ID: {employee.employee_id}")
            print(f"  Hourly Rate: {format_currency(float(employee.hourly_rate))}")

            if ask_continue("\nAdd another employee? [Y/N]: "):
                self.add_employee()

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Employee creation failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in add_employee: {str(e)}")
            input("Press Enter to continue...")

    def calculate_salary(self) -> None:
        """Calculate salary for an employee.
        
        Implements: SALARY = HOURLY_RATE × HOURS_WORKED
        """
        clear_screen()
        print_header("CALCULATE SALARY")

        try:
            # List employees first
            employees = self.employee_service.list_all_employees()
            if not employees:
                print("\nNo employees found.")
                input("Press Enter to continue...")
                return

            print("\nAvailable Employees:")
            for e in employees:
                print(f"  ID {e.id}: {e.name} ({e.employee_id}) - {format_currency(float(e.hourly_rate))}/hour")

            try:
                employee_id: int = int(input("\nEnter Employee ID: "))
            except ValueError:
                print("❌ Invalid employee ID")
                input("Press Enter to continue...")
                return

            employee = self.employee_service.get_employee_by_id(employee_id)

            try:
                hours_worked: float = float(input("Hours Worked: "))
            except ValueError:
                print("❌ Invalid hours format")
                input("Press Enter to continue...")
                return

            salary_record = self.employee_service.calculate_salary(
                employee_id=employee_id,
                hours_worked=hours_worked,
                admin_id=self.admin_id
            )

            print(f"\n✓ Salary calculated successfully!")
            print(f"  Employee: {employee.name}")
            print(f"  Hours Worked: {salary_record.hours_worked}")
            print(f"  Hourly Rate: {format_currency(float(salary_record.hourly_rate))}")
            print(f"  Total Salary: {format_currency(float(salary_record.total_salary))}")

            if ask_continue("\nCalculate another salary? [Y/N]: "):
                self.calculate_salary()

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Salary calculation failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in calculate_salary: {str(e)}")
            input("Press Enter to continue...")
