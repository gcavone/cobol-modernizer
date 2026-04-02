import logging
from decimal import Decimal
from typing import List, Optional
from repositories.product_repository import ProductRepository
from services.activity_service import ActivityService
from models.product import Product


class ProductService:
    """Service for managing product inventory.
    
    Handles CRUD operations for products with validation and activity logging.
    """

    def __init__(self, product_repo: ProductRepository, 
                 activity_service: ActivityService) -> None:
        """Initialize ProductService with repositories and services.
        
        Args:
            product_repo: Repository for product data access.
            activity_service: Service for logging activities.
        """
        self.product_repo: ProductRepository = product_repo
        self.activity_service: ActivityService = activity_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def create_product(self, code: str, name: str, unit: str, 
                      price: float, admin_id: int) -> Product:
        """Create a new product.
        
        Args:
            code: 8-digit product code (must be unique).
            name: Product name.
            unit: Unit of measurement (e.g., "155g", "1L").
            price: Unit price (must be > 0).
            admin_id: ID of admin creating the product.
        
        Returns:
            Created Product instance.
        
        Raises:
            ValueError: If validation fails or code already exists.
        """
        # Validate code format (8 digits)
        if not code or len(code) != 8 or not code.isdigit():
            raise ValueError("Product code must be exactly 8 digits")

        # Validate name
        if not name or len(name) < 2:
            raise ValueError("Product name must be at least 2 characters")

        # Validate unit
        if not unit or len(unit) < 1:
            raise ValueError("Unit of measurement is required")

        # Validate price
        try:
            price_decimal: Decimal = Decimal(str(price))
        except (ValueError, TypeError):
            raise ValueError("Price must be a valid number")

        if price_decimal <= 0:
            raise ValueError("Price must be greater than 0")

        # Check code uniqueness
        if self.product_repo.get_by_code(code):
            self.logger.warning(f"Product creation failed: code already exists - {code}")
            raise ValueError(f"Product code {code} already exists")

        # Create product
        product: Product = self.product_repo.create(
            code=code,
            name=name,
            unit=unit,
            price=float(price_decimal)
        )

        # Log activity
        self.activity_service.log_action(
            action="CREATE",
            entity_type="PRODUCT",
            entity_id=product.id,
            admin_id=admin_id,
            details=f"Code: {code}, Name: {name}, Price: {price_decimal}"
        )

        self.logger.info(f"Product created: {code} - {name}")

        return product

    def get_product_by_id(self, product_id: int) -> Product:
        """Retrieve a product by ID.
        
        Args:
            product_id: The product ID.
        
        Returns:
            Product instance.
        
        Raises:
            ValueError: If product not found.
        """
        product: Optional[Product] = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        return product

    def get_product_by_code(self, code: str) -> Product:
        """Retrieve a product by code.
        
        Args:
            code: The 8-digit product code.
        
        Returns:
            Product instance.
        
        Raises:
            ValueError: If product not found.
        """
        product: Optional[Product] = self.product_repo.get_by_code(code)
        if not product:
            raise ValueError(f"Product code {code} not found")
        return product

    def get_all_products(self) -> List[Product]:
        """Retrieve all products sorted by name.
        
        Returns:
            List of all Product instances.
        """
        return self.product_repo.get_all_sorted_by_name()

    def search_products_by_name(self, name: str) -> List[Product]:
        """Search products by name (case-insensitive).
        
        Args:
            name: Search term (partial match supported).
        
        Returns:
            List of matching Product instances.
        """
        if not name or len(name) < 1:
            raise ValueError("Search term must not be empty")
        return self.product_repo.search_by_name(name)

    def update_product(self, product_id: int, admin_id: int, **kwargs) -> Product:
        """Update an existing product.
        
        Args:
            product_id: The product ID to update.
            admin_id: ID of admin performing the update.
            **kwargs: Fields to update (code, name, unit, price).
        
        Returns:
            Updated Product instance.
        
        Raises:
            ValueError: If product not found or validation fails.
        """
        # Verify product exists
        product: Product = self.get_product_by_id(product_id)

        # Validate fields if provided
        if "code" in kwargs:
            code: str = kwargs["code"]
            if len(code) != 8 or not code.isdigit():
                raise ValueError("Product code must be exactly 8 digits")
            # Check uniqueness (excluding current product)
            existing: Optional[Product] = self.product_repo.get_by_code(code)
            if existing and existing.id != product_id:
                raise ValueError(f"Product code {code} already exists")

        if "name" in kwargs:
            name: str = kwargs["name"]
            if not name or len(name) < 2:
                raise ValueError("Product name must be at least 2 characters")

        if "price" in kwargs:
            try:
                price_decimal: Decimal = Decimal(str(kwargs["price"]))
            except (ValueError, TypeError):
                raise ValueError("Price must be a valid number")
            if price_decimal <= 0:
                raise ValueError("Price must be greater than 0")
            kwargs["price"] = float(price_decimal)

        # Update product
        updated_product: Optional[Product] = self.product_repo.update(product_id, **kwargs)

        # Log activity
        self.activity_service.log_action(
            action="UPDATE",
            entity_type="PRODUCT",
            entity_id=product_id,
            admin_id=admin_id,
            details=f"Updated fields: {', '.join(kwargs.keys())}"
        )

        self.logger.info(f"Product updated: {product_id}")

        return updated_product

    def delete_product(self, product_id: int, admin_id: int) -> bool:
        """Delete a product.
        
        Args:
            product_id: The product ID to delete.
            admin_id: ID of admin performing the deletion.
        
        Returns:
            True if deletion successful.
        
        Raises:
            ValueError: If product not found.
        """
        # Verify product exists
        product: Product = self.get_product_by_id(product_id)

        # Delete product
        success: bool = self.product_repo.delete(product_id)

        if success:
            # Log activity
            self.activity_service.log_action(
                action="DELETE",
                entity_type="PRODUCT",
                entity_id=product_id,
                admin_id=admin_id,
                details=f"Code: {product.code}, Name: {product.name}"
            )

            self.logger.info(f"Product deleted: {product_id}")

        return success
