from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from config import Config


class DatabaseConnection:
    """Manages database connection and session creation.
    
    Provides a singleton-like interface for obtaining database sessions.
    """

    _engine: Engine | None = None
    _session_factory: sessionmaker | None = None

    @classmethod
    def initialize(cls) -> None:
        """Initialize database connection and session factory.
        
        Should be called once at application startup.
        """
        if cls._engine is None:
            cls._engine = create_engine(
                Config.DATABASE_URL,
                echo=False,
                pool_pre_ping=True
            )
            cls._session_factory = sessionmaker(bind=cls._engine)

    @classmethod
    def get_session(cls) -> Session:
        """Get a new database session.
        
        Returns:
            SQLAlchemy Session instance.
        
        Raises:
            RuntimeError: If database not initialized.
        """
        if cls._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._session_factory()

    @classmethod
    def get_engine(cls) -> Engine:
        """Get the database engine.
        
        Returns:
            SQLAlchemy Engine instance.
        
        Raises:
            RuntimeError: If database not initialized.
        """
        if cls._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._engine

    @classmethod
    def close_session(cls, session: Session) -> None:
        """Close a database session.
        
        Args:
            session: The session to close.
        """
        if session:
            session.close()
