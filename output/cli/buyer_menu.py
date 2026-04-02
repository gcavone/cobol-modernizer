import logging
from typing import List
from services.product_service import ProductService
from services.order_service import OrderService
from cli.ui_helpers import clear_screen, print_header, print_table, format_currency


class BuyerMenu:
    """Buyer menu for customer shopping.
    
    Provides product browsing and order creation functionality.
    """

    def __init__(self, product_service: ProductService,
                 order_service: OrderService | None = None) -> None:
        """Initialize BuyerMenu with required services.
        
        Args:
            product_service: Service for product management.
            order_service: Service for order management (optional).
        """
        self.product_service: ProductService = product_service
        self.order_service: OrderService | None = order_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display buyer menu and handle selections.
        
        Loops until user chooses to exit.
        """
        while True:
            clear_screen()
            print_header("BUYER MENU")

            print("\n1) View Products")
            print("2) Create Order")
            print("3) Exit")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                self.view_products()
            elif choice == "2":
                if self.order_service:
                    self.create_order()
                else:
                    print("\n❌ Order service not available")
                    input("Press Enter to continue...")
            elif choice == "3":
                break
            else:
                print("\n❌ Invalid choice. Please select 1-3.")
                input("Press Enter to continue...")

    def view_products(self) -> None:
        """Display all available products in a formatted table."""
        clear_screen()
        print_header("AVAILABLE PRODUCTS")

        try:
            products = self.product_service.get_all_products()

            if not products:
                print("\nNo products available.")
                input("Press Enter to continue...")
                return

            headers: List[str] = ["Code", "Name", "Unit", "Price"]
            rows: List[List[str]] = [
                [
                    p.code,
                    p.name,
                    p.unit,
                    format_currency(float(p.price))
                ]
                for p in products
            ]

            print()
            print_table(headers, rows)
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\n❌ Error loading products: {str(e)}")
            self.logger.error(f"Error in view_products: {str(e)}")
            input("Press Enter to continue...")

    def create_order(self) -> None:
        """Guide user through order creation process."""
        clear_screen()
        print_header("CREATE ORDER")

        try:
            # Display available products
            products = self.product_service.get_all_products()
            if not products:
                print("\nNo products available for ordering.")
                input("Press Enter to continue...")
                return

            print("\nAvailable Products:")
            for p in products:
                print(f"  {p.code} - {p.name} ({p.unit}) - {format_currency(float(p.price))}")

            # Get number of items
            try:
                num_items: int = int(input("\nHow many items to order? "))
                if num_items <= 0 or num_items > 100:
                    print("❌ Number of items must be between 1 and 100")
                    input("Press Enter to continue...")
                    return
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                input("Press Enter to continue...")
                return

            # Collect order items
            from services.order_service import OrderItemData
            from decimal import Decimal

            items: List[OrderItemData] = []
            total: Decimal = Decimal('0')

            for i in range(num_items):
                print(f"\n--- Item {i + 1} ---")
                code: str = input("Product Code: ").strip()

                try:
                    product = self.product_service.get_product_by_code(code)
                except ValueError:
                    print(f"❌ Product code {code} not found")
                    continue

                try:
                    quantity: int = int(input("Quantity: "))
                    if quantity <= 0:
                        print("❌ Quantity must be positive")
                        continue
                except ValueError:
                    print("❌ Invalid quantity")
                    continue

                unit_price: Decimal = Decimal(str(product.price))
                subtotal: Decimal = Decimal(quantity) * unit_price
                total += subtotal

                items.append(OrderItemData(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price
                ))

                print(f"✓ Added: {product.name} x{quantity} = {format_currency(float(subtotal))}")

            if not items:
                print("\n❌ No items added to order")
                input("Press Enter to continue...")
                return

            # Display order summary
            print("\n" + "=" * 60)
            print("ORDER SUMMARY")
            print("=" * 60)
            print(f"Total Amount: {format_currency(float(total))}")

            # Get payment
            try:
                payment: float = float(input("\nAmount Paid: "))
                if payment <= 0:
                    print("❌ Payment must be positive")
                    input("Press Enter to continue...")
                    return
            except ValueError:
                print("❌ Invalid payment amount")
                input("Press Enter to continue...")
                return

            # Create order
            order_result = self.order_service.create_order(
                items=items,
                payment_amount=Decimal(str(payment))
            )

            # Display receipt
            self._print_receipt(order_result)

        except Exception as e:
            print(f"\n❌ Error creating order: {str(e)}")
            self.logger.error(f"Error in create_order: {str(e)}")
            input("Press Enter to continue...")

    def _print_receipt(self, order_result: dict) -> None:
        """Print order receipt.
        
        Args:
            order_result: Dictionary with order details.
        """
        clear_screen()
        print("=" * 60)
        print("RECEIPT".center(60))
        print("=" * 60)

        order = order_result["order"]
        items = order_result["items"]

        print(f"\nOrder Number: {order.order_number}")
        print(f"Date/Time: {order.created_at}")

        print("\n" + "-" * 60)
        print("Items:")
        print("-" * 60)

        for item in items:
            product = self.product_service.get_product_by_id(item.product_id)
            print(
                f"{product.name:30} x{item.quantity:3} @ {format_currency(float(item.unit_price)):>10} = {format_currency(float(item.subtotal)):>10}"
            )

        print("-" * 60)
        print(f"Total Amount:    {format_currency(order_result['total_amount']):>50}")
        print(f"Amount Paid:     {format_currency(order_result['payment_amount']):>50}")
        print(f"Change:          {format_currency(order_result['change_amount']):>50}")
        print("=" * 60)
        print("THANK YOU FOR SHOPPING!".center(60))
        print("=" * 60)

        input("\nPress Enter to continue...")
