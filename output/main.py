import logging
import logging.handlers
from config import Config
from database.connection import DatabaseConnection
from database.init_db import init_database
from repositories.product_repository import ProductRepository
from repositories.admin_repository import AdminRepository
from repositories.employee_repository import EmployeeRepository
from repositories.order_repository import OrderRepository
from repositories.order_item_repository import OrderItemRepository
from repositories.salary_repository import SalaryRepository
from repositories.profit_repository import ProfitRepository
from repositories.activity_log_repository import ActivityLogRepository
from services.auth_service import AuthService
from services.product_service import ProductService
from services.employee_service import EmployeeService
from services.order_service import OrderService
from services.profit_service import ProfitService
from services.activity_service import ActivityService
from cli.main_menu import MainMenu


def setup_logging() -> None:
    """Configure logging with rotating file handler.
    
    Sets up logging to both console and file with appropriate formatting.
    """
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)

    # Configure root logger
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(Config.LOG_LEVEL)

    # File handler with rotation
    file_handler: logging.handlers.RotatingFileHandler = (
        logging.handlers.RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
    )
    file_handler.setLevel(Config.LOG_LEVEL)

    # Console handler
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Formatter
    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging initialized")


def main() -> None:
    """Main application entry point.
    
    Initializes configuration, database, repositories, services,
    and starts the CLI interface.
    """
    try:
        # Validate configuration
        Config.validate()

        # Setup logging
        setup_logging()
        logger: logging.Logger = logging.getLogger(__name__)
        logger.info("Application starting...")

        # Initialize database connection
        DatabaseConnection.initialize()
        logger.info("Database connection initialized")

        # Initialize database (create tables and seed data)
        init_database()
        logger.info("Database initialized")

        # Get database session
        session = DatabaseConnection.get_session()

        # Initialize repositories
        product_repo: ProductRepository = ProductRepository(session)
        admin_repo: AdminRepository = AdminRepository(session)
        employee_repo: EmployeeRepository = EmployeeRepository(session)
        order_repo: OrderRepository = OrderRepository(session)
        order_item_repo: OrderItemRepository = OrderItemRepository(session)
        salary_repo: SalaryRepository = SalaryRepository(session)
        profit_repo: ProfitRepository = ProfitRepository(session)
        activity_log_repo: ActivityLogRepository = ActivityLogRepository(session)

        logger.info("Repositories initialized")

        # Initialize services
        activity_service: ActivityService = ActivityService(activity_log_repo)
        auth_service: AuthService = AuthService(admin_repo)
        product_service: ProductService = ProductService(product_repo, activity_service)
        employee_service: EmployeeService = EmployeeService(
            employee_repo, salary_repo, activity_service
        )
        order_service: OrderService = OrderService(
            order_repo, order_item_repo, product_repo, activity_service
        )
        profit_service: ProfitService = ProfitService(profit_repo, activity_service)

        logger.info("Services initialized")

        # Create and display main menu
        main_menu: MainMenu = MainMenu(
            auth_service=auth_service,
            product_service=product_service,
            employee_service=employee_service,
            order_service=order_service,
            profit_service=profit_service,
        )
        main_menu.display()

        # Cleanup
        DatabaseConnection.close_session(session)
        logger.info("Application terminated normally")

    except ValueError as e:
        print(f"Configuration Error: {str(e)}")
        logging.error(f"Configuration error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()