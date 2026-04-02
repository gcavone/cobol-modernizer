from sqlalchemy.orm import Session
from typing import Optional, List
from models.product import Product
from repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Repository for managing Product entities.
    
    Provides specialized query methods for products beyond the base CRUD operations.
    """

    def __init__(self, session: Session) -> None:
        """Initialize ProductRepository with database session.
        
        Args:
            session: SQLAlchemy database session.
        """
        super().__init__(session, Product)

    def get_by_code(self, code: str) -> Optional[Product]:
        """Retrieve a product by its 8-digit code.
        
        Args:
            code: The product code (e.g., "00000001").
        
        Returns:
            The Product instance if found, None otherwise.
        """
        return self.session.query(Product).filter(
            Product.code == code
        ).first()

    def get_all_sorted_by_name(self) -> List[Product]:
        """Retrieve all products sorted alphabetically by name.
        
        Returns:
            List of all Product instances ordered by name.
        """
        return self.session.query(Product).order_by(Product.name).all()

    def search_by_name(self, name: str) -> List[Product]:
        """Search for products by name using case-insensitive pattern matching.
        
        Args:
            name: The search term (partial name match supported).
        
        Returns:
            List of Product instances matching the search term.
        """
        return self.session.query(Product).filter(
            Product.name.ilike(f"%{name}%")
        ).all()
