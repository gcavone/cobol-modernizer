import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "supermarket_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL",
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "logs/app.log"

    # Application Configuration
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "robby@gmail.com")
    DEFAULT_HOURLY_RATE: float = 500.0
    MAX_HOURS_PER_DAY: float = 24.0
    MIN_PASSWORD_LENGTH: int = 6
    BCRYPT_ROUNDS: int = 12

    @classmethod
    def validate(cls) -> None:
        """Validate critical configuration values."""
        if not cls.DB_HOST:
            raise ValueError("DB_HOST environment variable is required")
        if not cls.DB_NAME:
            raise ValueError("DB_NAME environment variable is required")
        if not cls.DB_USER:
            raise ValueError("DB_USER environment variable is required")