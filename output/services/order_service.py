import logging
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from repositories.order_repository import OrderRepository
from repositories.order_item_repository import OrderItemRepository
from repositories.product_repository import ProductRepository
from services.activity_service import ActivityService
from models.order import Order
from models.order_item import OrderItem


@dataclass
class OrderItemData:
    """Data class for order item input.
    
    Attributes:
        product_id: ID of the product.
        quantity: Number of units ordered.
        unit_price: Price per unit.
    """
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderService:
    """Service for managing customer orders.
    
    Handles order creation, item management, and implements
    the business rule: CHANGE = PAYMENT - TOTAL
    """

    def __init__(self, order_repo: OrderRepository,
                 order_item_repo: OrderItemRepository,
                 product_repo: ProductRepository,
                 activity_service: ActivityService) -> None:
        """Initialize OrderService with repositories and services.
        
        Args:
            order_repo: Repository for order data access.
            order_item_repo: Repository for order item data access.
            product_repo: Repository for product data access.
            activity_service: Service for logging activities.
        """
        self.order_repo: OrderRepository = order_repo
        self.order_item_repo: OrderItemRepository = order_item_repo
        self.product_repo: ProductRepository = product_repo
        self.activity_service: ActivityService = activity_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def create_order(self, items: List[OrderItemData], 
                    payment_amount: Decimal, admin_id: int | None = None) -> dict:
        """Create a new customer order.
        
        Implements order creation flow:
        1. Validate items and payment
        2. Calculate total amount
        3. Save order and items to database
        4. Calculate change: CHANGE = PAYMENT - TOTAL
        5. Log activity
        
        Args:
            items: List of OrderItemData (product_id, quantity, unit_price).
            payment_amount: Amount paid by customer.
            admin_id: ID of admin creating order (optional).
        
        Returns:
            Dictionary with order, items, total_amount, payment_amount, change_amount.
        
        Raises:
            ValueError: If items invalid, payment insufficient, or product not found.
        """
        # Validate items list
        if not items or len(items) == 0:
            raise ValueError("Order must contain at least one item")

        if len(items) > 100:
            raise ValueError("Order cannot contain more than 100 items")

        # Validate payment amount
        try:
            payment_decimal: Decimal = Decimal(str(payment_amount))
        except (ValueError, TypeError):
            raise ValueError("Payment amount must be a valid number")

        if payment_decimal <= 0:
            raise ValueError("Payment amount must be positive")

        # Calculate total and validate items
        total_amount: Decimal = Decimal('0')
        validated_items: List[tuple] = []

        for item in items:
            # Validate quantity
            if item.quantity <= 0:
                raise ValueError("Quantity must be positive")

            # Validate unit price
            try:
                unit_price: Decimal = Decimal(str(item.unit_price))
            except (ValueError, TypeError):
                raise ValueError("Unit price must be a valid number")

            if unit_price <= 0:
                raise ValueError("Unit price must be positive")

            # Verify product exists
            product: Optional[Order] = self.product_repo.get_by_id(item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")

            # Calculate subtotal
            subtotal: Decimal = Decimal(item.quantity) * unit_price
            total_amount += subtotal

            validated_items.append((item, unit_price, subtotal))

        # Validate payment >= total
        if payment_decimal < total_amount:
            raise ValueError(
                f"Insufficient payment. Total: {total_amount}, "
                f"Paid: {payment_decimal}"
            )

        # Calculate change: CHANGE = PAYMENT - TOTAL
        change_amount: Decimal = payment_decimal - total_amount

        # Create order
        order: Order = self.order_repo.create(
            order_number=self._generate_order_number(),
            total_amount=float(total_amount),
            payment_amount=float(payment_decimal),
            change_amount=float(change_amount)
        )

        # Create order items
        order_items: List[OrderItem] = []
        for item, unit_price, subtotal in validated_items:
            order_item: OrderItem = self.order_item_repo.create(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=float(unit_price),
                subtotal=float(subtotal)
            )
            order_items.append(order_item)

        # Log activity
        self.activity_service.log_action(
            action="ORDER_CREATED",
            entity_type="ORDER",
            entity_id=order.id,
            admin_id=admin_id,
            details=f"Total: {total_amount}, Items: {len(items)}, Change: {change_amount}"
        )

        self.logger.info(
            f"Order created: {order.order_number} - "
            f"Total: {total_amount}, Change: {change_amount}"
        )

        return {
            "order": order,
            "items": order_items,
            "total_amount": float(total_amount),
            "payment_amount": float(payment_decimal),
            "change_amount": float(change_amount)
        }

    def calculate_change(self, total_amount: Decimal, 
                        payment_amount: Decimal) -> Decimal:
        """Calculate change amount.
        
        Implements business rule: CHANGE = PAYMENT - TOTAL
        
        Args:
            total_amount: Total order amount.
            payment_amount: Amount paid by customer.
        
        Returns:
            Change amount.
        
        Raises:
            ValueError: If payment is insufficient.
        """
        try:
            total: Decimal = Decimal(str(total_amount))
            payment: Decimal = Decimal(str(payment_amount))
        except (ValueError, TypeError):
            raise ValueError("Amounts must be valid numbers")

        if payment < total:
            raise ValueError(
                f"Insufficient payment. Total: {total}, Paid: {payment}"
            )

        return payment - total

    def get_order_receipt(self, order_id: int) -> dict:
        """Retrieve order receipt with details.
        
        Args:
            order_id: The order ID.
        
        Returns:
            Dictionary with order details and items.
        
        Raises:
            ValueError: If order not found.
        """
        order: Optional[Order] = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        items: List[OrderItem] = self.order_item_repo.get_by_order_id(order_id)

        return {
            "order_number": order.order_number,
            "created_at": order.created_at,
            "items": items,
            "total_amount": order.total_amount,
            "payment_amount": order.payment_amount,
            "change_amount": order.change_amount
        }

    def get_order_by_id(self, order_id: int) -> Order:
        """Retrieve an order by ID.
        
        Args:
            order_id: The order ID.
        
        Returns:
            Order instance.
        
        Raises:
            ValueError: If order not found.
        """
        order: Optional[Order] = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        return order

    def list_all_orders(self) -> List[Order]:
        """Retrieve all orders sorted by date (newest first).
        
        Returns:
            List of all Order instances.
        """
        return self.order_repo.get_all_sorted_by_date()

    @staticmethod
    def _generate_order_number() -> str:
        """Generate unique order number.
        
        Returns:
            Order number string (format: ORD-YYYYMMDDHHmmss).
        """
        return f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
