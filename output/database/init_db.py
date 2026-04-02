from sqlalchemy.orm import sessionmaker
from config import Config
from database.connection import DatabaseConnection
from models.product import Product
from models.admin import Admin
from models.employee import Employee
from models.order import Order
from models.order_item import OrderItem
from models.salary_record import SalaryRecord
from models.profit_record import ProfitRecord
from models.activity_log import ActivityLog
from models.product import Base
from repositories.product_repository import ProductRepository
from repositories.admin_repository import AdminRepository
from repositories.employee_repository import EmployeeRepository
from services.auth_service import AuthService


def init_database() -> None:
    """Initialize database: create tables and seed default data.
    
    Creates all tables and populates with default admin, products, and employees.
    """
    # Initialize database connection
    DatabaseConnection.initialize()
    engine = DatabaseConnection.get_engine()

    # Create all tables
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully")

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create default admin
        admin_repo = AdminRepository(session)
        default_email = "robby@gmail.com"

        if not admin_repo.get_by_email(default_email):
            password_hash = AuthService.hash_password("robby@123")
            admin_repo.create(
                email=default_email,
                password_hash=password_hash,
                is_active=True
            )
            print(f"✓ Default admin created: {default_email}")
        else:
            print(f"✓ Default admin already exists: {default_email}")

        # Create sample products
        product_repo = ProductRepository(session)
        sample_products = [
            {
                "code": "00000001",
                "name": "Canned Sardines",
                "unit": "155g",
                "price": 18.75
            },
            {
                "code": "00000002",
                "name": "Canned Sardines Spicy",
                "unit": "155g",
                "price": 18.75
            },
            {
                "code": "00000003",
                "name": "Condensed Milk",
                "unit": "300mL",
                "price": 53.00
            },
            {
                "code": "00000004",
                "name": "Evaporated Milk",
                "unit": "410mL",
                "price": 44.00
            },
            {
                "code": "00000005",
                "name": "Powdered Milk",
                "unit": "300g",
                "price": 96.25
            },
            {
                "code": "00000006",
                "name": "Cooking Oil",
                "unit": "1L",
                "price": 125.50
            },
            {
                "code": "00000007",
                "name": "Rice",
                "unit": "2kg",
                "price": 85.00
            },
            {
                "code": "00000008",
                "name": "Sugar",
                "unit": "1kg",
                "price": 45.00
            },
        ]

        created_count = 0
        for prod in sample_products:
            if not product_repo.get_by_code(prod["code"]):
                product_repo.create(**prod)
                created_count += 1

        print(f"✓ {created_count} sample products created")

        # Create sample employees
        employee_repo = EmployeeRepository(session)
        sample_employees = [
            {
                "name": "Juan Dela Cruz",
                "employee_id": "EMP001",
                "hourly_rate": 500.00
            },
            {
                "name": "Maria Santos",
                "employee_id": "EMP002",
                "hourly_rate": 500.00
            },
            {
                "name": "Pedro Reyes",
                "employee_id": "EMP003",
                "hourly_rate": 550.00
            },
            {
                "name": "Ana Garcia",
                "employee_id": "EMP004",
                "hourly_rate": 500.00
            },
        ]

        created_emp_count = 0
        for emp in sample_employees:
            if not employee_repo.get_by_employee_id(emp["employee_id"]):
                employee_repo.create(**emp)
                created_emp_count += 1

        print(f"✓ {created_emp_count} sample employees created")

        print("\n✓ Database initialization completed successfully!")

    except Exception as e:
        print(f"✗ Error during database initialization: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
