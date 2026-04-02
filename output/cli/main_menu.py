import logging
from services.auth_service import AuthService
from services.product_service import ProductService
from services.employee_service import EmployeeService
from services.order_service import OrderService
from services.profit_service import ProfitService
from cli.admin_menu import AdminMenu
from cli.buyer_menu import BuyerMenu
from cli.ui_helpers import clear_screen, print_header


class MainMenu:
    """Main menu for the supermarket management system.
    
    Provides entry point for administrators and buyers.
    """

    def __init__(self, auth_service: AuthService,
                 product_service: ProductService,
                 employee_service: EmployeeService | None = None,
                 order_service: OrderService | None = None,
                 profit_service: ProfitService | None = None) -> None:
        """Initialize MainMenu with required services.
        
        Args:
            auth_service: Service for authentication.
            product_service: Service for product management.
            employee_service: Service for employee management.
            order_service: Service for order management.
            profit_service: Service for profit calculation.
        """
        self.auth_service: AuthService = auth_service
        self.product_service: ProductService = product_service
        self.employee_service: EmployeeService | None = employee_service
        self.order_service: OrderService | None = order_service
        self.profit_service: ProfitService | None = profit_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display main menu and handle user selection.
        
        Loops until user chooses to exit.
        """
        while True:
            clear_screen()
            print_header("SUPERMARKET MANAGEMENT SYSTEM")

            print("\n1) Administrator")
            print("2) Buyer")
            print("3) Exit")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                self._admin_login()
            elif choice == "2":
                buyer_menu = BuyerMenu(self.product_service)
                buyer_menu.display()
            elif choice == "3":
                print("\nThank you for using the system. Goodbye!")
                self.logger.info("Application terminated by user")
                break
            else:
                print("\n❌ Invalid choice. Please select 1, 2, or 3.")
                input("Press Enter to continue...")

    def _admin_login(self) -> None:
        """Handle administrator login.
        
        Prompts for email and password, authenticates, and displays admin menu.
        """
        clear_screen()
        print_header("ADMINISTRATOR LOGIN")

        email: str = input("\nEmail: ").strip()
        password: str = input("Password: ").strip()

        try:
            admin = self.auth_service.authenticate(email, password)
            print(f"\n✓ Welcome, {admin.email}!")
            input("Press Enter to continue...")

            admin_menu = AdminMenu(
                auth_service=self.auth_service,
                product_service=self.product_service,
                employee_service=self.employee_service,
                order_service=self.order_service,
                profit_service=self.profit_service,
                admin_id=admin.id
            )
            admin_menu.display()

        except ValueError as e:
            print(f"\n❌ Login failed: {str(e)}")
            self.logger.warning(f"Failed login attempt for email: {email}")
            input("Press Enter to continue...")