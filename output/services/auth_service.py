import bcrypt
import logging
from datetime import datetime
from repositories.admin_repository import AdminRepository
from models.admin import Admin


class AuthService:
    """Service for authentication and password management.
    
    Handles admin authentication, password hashing with bcrypt,
    and admin account creation.
    """

    def __init__(self, admin_repo: AdminRepository) -> None:
        """Initialize AuthService with admin repository.
        
        Args:
            admin_repo: Repository for admin data access.
        """
        self.admin_repo: AdminRepository = admin_repo
        self.logger: logging.Logger = logging.getLogger(__name__)

    def authenticate(self, email: str, password: str) -> Admin:
        """Authenticate an admin with email and password.
        
        Validates credentials against bcrypt hash stored in database
        and updates last_login timestamp on successful authentication.
        
        Args:
            email: Admin email address.
            password: Admin password (plaintext).
        
        Returns:
            Admin instance if authentication successful.
        
        Raises:
            ValueError: If email/password invalid or account inactive.
        """
        # Validate input
        if not email or not password:
            self.logger.warning("Authentication attempt with missing credentials")
            raise ValueError("Email and password are required")

        # Retrieve admin from database
        admin: Admin | None = self.admin_repo.get_by_email(email)
        if not admin:
            self.logger.warning(f"Authentication failed: email not found - {email}")
            raise ValueError("Invalid email or password")

        if not admin.is_active:
            self.logger.warning(f"Authentication failed: account inactive - {email}")
            raise ValueError("Account is inactive")

        # Verify password with bcrypt
        try:
            if not bcrypt.checkpw(password.encode(), admin.password_hash.encode()):
                self.logger.warning(f"Authentication failed: invalid password - {email}")
                raise ValueError("Invalid email or password")
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise ValueError(f"Authentication error: {str(e)}")

        # Update last login
        self.admin_repo.update(admin.id, last_login=datetime.utcnow())
        self.logger.info(f"Admin authenticated successfully: {email}")

        return admin

    @staticmethod
    def hash_password(password: str) -> str:
        """Generate bcrypt hash of a password.
        
        Args:
            password: Plaintext password to hash.
        
        Returns:
            Bcrypt hash string.
        
        Raises:
            ValueError: If password is too short (< 6 characters).
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        salt: bytes = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()

    def create_admin(self, email: str, password: str) -> dict:
        """Create a new admin account with hashed password.
        
        Args:
            email: Admin email address (must be unique).
            password: Admin password (will be hashed).
        
        Returns:
            Dictionary with id and email of created admin.
        
        Raises:
            ValueError: If email invalid, already exists, or password too short.
        """
        # Validate email format
        if not email or "@" not in email:
            raise ValueError("Invalid email format")

        # Check email uniqueness
        if self.admin_repo.get_by_email(email):
            self.logger.warning(f"Admin creation failed: email already exists - {email}")
            raise ValueError("Email already exists")

        # Hash password
        password_hash: str = self.hash_password(password)

        # Create admin
        admin: Admin = self.admin_repo.create(
            email=email,
            password_hash=password_hash,
            is_active=True
        )

        self.logger.info(f"New admin created: {email}")

        return {"id": admin.id, "email": admin.email}
