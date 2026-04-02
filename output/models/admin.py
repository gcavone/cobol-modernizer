from sqlalchemy import Column, Integer, String, Boolean, DateTime
from models.product import Base
from datetime import datetime


class Admin(Base):
    """Represents an administrator user with authentication credentials.
    
    Attributes:
        id: Unique admin identifier (auto-increment).
        email: Admin email address (unique).
        password_hash: Bcrypt hash of admin password.
        is_active: Whether the admin account is active.
        created_at: Timestamp of admin account creation.
        last_login: Timestamp of last successful login.
    """

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """Return string representation of Admin."""
        return (
            f"<Admin(id={self.id}, email={self.email}, "
            f"is_active={self.is_active}, last_login={self.last_login})>"
        )