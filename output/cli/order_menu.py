import logging
from typing import List
from services.order_service import OrderService
from cli.ui_helpers import clear_screen, print_header, print_table, format_currency


class OrderMenu:
    """Order viewing menu for administrators.
    
    Provides order history and receipt viewing operations.
    """

    def __init__(self, order_service: OrderService) -> None:
        """Initialize OrderMenu with required services.
        
        Args:
            order_service: Service for order management.
        """
        self.order_service: OrderService = order_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display order menu and handle selections.
        
        Loops until user chooses to exit.
        """
        while True:
            clear_screen()
            print_header("ORDER MANAGEMENT")

            print("\n1) View All Orders")
            print("2) View Order Receipt")
            print("3) Back to Admin Menu")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                self.list_orders()
            elif choice == "2":
                self.view_order_receipt()
            elif choice == "3":
                break
            else:
                print("\n❌ Invalid choice. Please select 1-3.")
                input("Press Enter to continue...")

    def list_orders(self) -> None:
        """Display all orders in a formatted table."""
        clear_screen()
        print_header("ORDER HISTORY")

        try:
            orders = self.order_service.list_all_orders()

            if not orders:
                print("\nNo orders found.")
                input("Press Enter to continue...")
                return

            headers: List[str] = ["Order #", "Total", "Paid", "Change", "Date"]
            rows: List[List[str]] = [
                [
                    o.order_number,
                    format_currency(float(o.total_amount)),
                    format_currency(float(o.payment_amount)),
                    format_currency(float(o.change_amount)),
                    str(o.created_at)
                ]
                for o in orders
            ]

            print()
            print_table(headers, rows)
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\n❌ Error loading orders: {str(e)}")
            self.logger.error(f"Error in list_orders: {str(e)}")
            input("Press Enter to continue...")

    def view_order_receipt(self) -> None:
        """Display a specific order receipt."""
        clear_screen()
        print_header("VIEW ORDER RECEIPT")

        try:
            try:
                order_id: int = int(input("\nEnter Order ID: "))
            except ValueError:
                print("❌ Invalid order ID")
                input("Press Enter to continue...")
                return

            receipt = self.order_service.get_order_receipt(order_id)

            self._print_receipt(receipt)

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Receipt retrieval failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in view_order_receipt: {str(e)}")
            input("Press Enter to continue...")

    def _print_receipt(self, receipt: dict) -> None:
        """Print order receipt.
        
        Args:
            receipt: Dictionary with order details.
        """
        clear_screen()
        print("=" * 70)
        print("RECEIPT".center(70))
        print("=" * 70)

        print(f"\nOrder Number: {receipt['order_number']}")
        print(f"Date/Time: {receipt['created_at']}")

        print("\n" + "-" * 70)
        print("Items:")
        print("-" * 70)

        for item in receipt["items"]:
            print(
                f"Product ID {item.product_id:3} x{item.quantity:3} @ {format_currency(float(item.unit_price)):>10} = {format_currency(float(item.subtotal)):>10}"
            )

        print("-" * 70)
        print(f"Total Amount:    {format_currency(receipt['total_amount']):>55}")
        print(f"Amount Paid:     {format_currency(receipt['payment_amount']):>55}")
        print(f"Change:          {format_currency(receipt['change_amount']):>55}")
        print("=" * 70)
        print("THANK YOU FOR SHOPPING!".center(70))
        print("=" * 70)

        input("\nPress Enter to continue...")
