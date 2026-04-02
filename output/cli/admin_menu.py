import logging
from services.auth_service import AuthService
from services.product_service import ProductService
from services.employee_service import EmployeeService
from services.order_service import OrderService
from services.profit_service import ProfitService
from cli.product_menu import ProductMenu
from cli.employee_menu import EmployeeMenu
from cli.profit_menu import ProfitMenu
from cli.order_menu import OrderMenu
from cli.ui_helpers import clear_screen, print_header


class AdminMenu:
    """Administrator menu for system management.
    
    Provides access to product, employee, profit, and order management.
    """

    def __init__(self, auth_service: AuthService,
                 product_service: ProductService,
                 employee_service: EmployeeService | None = None,
                 order_service: OrderService | None = None,
                 profit_service: ProfitService | None = None,
                 admin_id: int | None = None) -> None:
        """Initialize AdminMenu with required services.
        
        Args:
            auth_service: Service for authentication.
            product_service: Service for product management.
            employee_service: Service for employee management (optional).
            order_service: Service for order management (optional).
            profit_service: Service for profit calculation (optional).
            admin_id: ID of logged-in administrator.
        """
        self.auth_service: AuthService = auth_service
        self.product_service: ProductService = product_service
        self.employee_service: EmployeeService | None = employee_service
        self.order_service: OrderService | None = order_service
        self.profit_service: ProfitService | None = profit_service
        self.admin_id: int | None = admin_id
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display administrator menu and handle selections.
        
        Loops until user chooses to logout.
        """
        while True:
            clear_screen()
            print_header("ADMINISTRATOR MENU")

            print("\n1) Manage Products")
            print("2) Manage Employees")
            print("3) Calculate Profit")
            print("4) View Orders")
            print("5) Logout")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                product_menu = ProductMenu(self.product_service, self.admin_id)
                product_menu.display()
            elif choice == "2":
                if self.employee_service:
                    employee_menu = EmployeeMenu(self.employee_service, self.admin_id)
                    employee_menu.display()
                else:
                    print("\n❌ Employee service not available")
                    input("Press Enter to continue...")
            elif choice == "3":
                if self.profit_service:
                    profit_menu = ProfitMenu(self.profit_service, self.admin_id)
                    profit_menu.display()
                else:
                    print("\n❌ Profit service not available")
                    input("Press Enter to continue...")
            elif choice == "4":
                if self.order_service:
                    order_menu = OrderMenu(self.order_service)
                    order_menu.display()
                else:
                    print("\n❌ Order service not available")
                    input("Press Enter to continue...")
            elif choice == "5":
                print("\n✓ Logged out successfully")
                self.logger.info(f"Admin {self.admin_id} logged out")
                break
            else:
                print("\n❌ Invalid choice. Please select 1-5.")
                input("Press Enter to continue...")
