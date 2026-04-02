import logging
from typing import List
from services.profit_service import ProfitService
from cli.ui_helpers import clear_screen, print_header, ask_continue, print_table, format_currency


class ProfitMenu:
    """Profit management menu for administrators.
    
    Provides profit calculation and viewing operations.
    """

    def __init__(self, profit_service: ProfitService, admin_id: int) -> None:
        """Initialize ProfitMenu with required services.
        
        Args:
            profit_service: Service for profit calculation.
            admin_id: ID of logged-in administrator.
        """
        self.profit_service: ProfitService = profit_service
        self.admin_id: int = admin_id
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display profit menu and handle selections.
        
        Loops until user chooses to exit.
        """
        while True:
            clear_screen()
            print_header("PROFIT MANAGEMENT")

            print("\n1) Calculate Profit")
            print("2) View Profit History")
            print("3) Back to Admin Menu")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                self.calculate_profit()
            elif choice == "2":
                self.list_profits()
            elif choice == "3":
                break
            else:
                print("\n❌ Invalid choice. Please select 1-3.")
                input("Press Enter to continue...")

    def calculate_profit(self) -> None:
        """Calculate profit.
        
        Implements: PROFIT = SELLING_PRICE - COGS
        """
        clear_screen()
        print_header("CALCULATE PROFIT")

        try:
            try:
                cogs: float = float(input("\nCost of Goods Sold (COGS): "))
            except ValueError:
                print("❌ Invalid COGS format")
                input("Press Enter to continue...")
                return

            try:
                selling_price: float = float(input("Selling Price: "))
            except ValueError:
                print("❌ Invalid selling price format")
                input("Press Enter to continue...")
                return

            profit_record = self.profit_service.calculate_profit(
                cogs=cogs,
                selling_price=selling_price,
                admin_id=self.admin_id
            )

            print(f"\n✓ Profit calculated successfully!")
            print(f"  COGS: {format_currency(float(profit_record.cogs))}")
            print(f"  Selling Price: {format_currency(float(profit_record.selling_price))}")
            print(f"  Profit: {format_currency(float(profit_record.profit))}")

            if ask_continue("\nCalculate another profit? [Y/N]: "):
                self.calculate_profit()

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Profit calculation failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in calculate_profit: {str(e)}")
            input("Press Enter to continue...")

    def list_profits(self) -> None:
        """Display all profit records in a formatted table."""
        clear_screen()
        print_header("PROFIT HISTORY")

        try:
            profits = self.profit_service.list_all_profits()

            if not profits:
                print("\nNo profit records found.")
                input("Press Enter to continue...")
                return

            headers: List[str] = ["ID", "COGS", "Selling Price", "Profit", "Date"]
            rows: List[List[str]] = [
                [
                    str(p.id),
                    format_currency(float(p.cogs)),
                    format_currency(float(p.selling_price)),
                    format_currency(float(p.profit)),
                    str(p.created_at)
                ]
                for p in profits
            ]

            print()
            print_table(headers, rows)
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\n❌ Error loading profit records: {str(e)}")
            self.logger.error(f"Error in list_profits: {str(e)}")
            input("Press Enter to continue...")
