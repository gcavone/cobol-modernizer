from sqlalchemy.orm import Session
from typing import List, Optional, Type, TypeVar

T = TypeVar('T')


class BaseRepository:
    """Base repository class providing generic CRUD operations.
    
    This class provides a foundation for all repository implementations,
    offering standard Create, Read, Update, Delete operations that work
    with any SQLAlchemy model class.
    """

    def __init__(self, session: Session, model_class: Type[T]) -> None:
        """Initialize repository with database session and model class.
        
        Args:
            session: SQLAlchemy database session.
            model_class: The SQLAlchemy model class this repository manages.
        """
        self.session: Session = session
        self.model_class: Type[T] = model_class

    def create(self, **kwargs) -> T:
        """Create and persist a new record.
        
        Args:
            **kwargs: Keyword arguments matching model attributes.
        
        Returns:
            The created model instance.
        
        Raises:
            Exception: If database operation fails.
        """
        obj: T = self.model_class(**kwargs)
        self.session.add(obj)
        self.session.commit()
        return obj

    def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve a record by its primary key.
        
        Args:
            id: The primary key value.
        
        Returns:
            The model instance if found, None otherwise.
        """
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()

    def get_all(self) -> List[T]:
        """Retrieve all records of this model type.
        
        Returns:
            List of all model instances.
        """
        return self.session.query(self.model_class).all()

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing record.
        
        Args:
            id: The primary key of the record to update.
            **kwargs: Keyword arguments with new values.
        
        Returns:
            The updated model instance if found, None otherwise.
        """
        obj: Optional[T] = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.session.commit()
        return obj

    def delete(self, id: int) -> bool:
        """Delete a record by its primary key.
        
        Args:
            id: The primary key of the record to delete.
        
        Returns:
            True if deletion was successful, False if record not found.
        """
        obj: Optional[T] = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False