import logging
from typing import List
from services.product_service import ProductService
from cli.ui_helpers import clear_screen, print_header, ask_continue, print_table, format_currency


class ProductMenu:
    """Product management menu for administrators.
    
    Provides CRUD operations for product inventory.
    """

    def __init__(self, product_service: ProductService, admin_id: int) -> None:
        """Initialize ProductMenu with required services.
        
        Args:
            product_service: Service for product management.
            admin_id: ID of logged-in administrator.
        """
        self.product_service: ProductService = product_service
        self.admin_id: int = admin_id
        self.logger: logging.Logger = logging.getLogger(__name__)

    def display(self) -> None:
        """Display product menu and handle selections.
        
        Loops until user chooses to exit.
        """
        while True:
            clear_screen()
            print_header("PRODUCT MANAGEMENT")

            print("\n1) List Products")
            print("2) Add Product")
            print("3) Update Product")
            print("4) Delete Product")
            print("5) Search Product")
            print("6) Back to Admin Menu")

            choice: str = input("\nSelect option: ").strip()

            if choice == "1":
                self.list_products()
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.update_product()
            elif choice == "4":
                self.delete_product()
            elif choice == "5":
                self.search_product()
            elif choice == "6":
                break
            else:
                print("\n❌ Invalid choice. Please select 1-6.")
                input("Press Enter to continue...")

    def list_products(self) -> None:
        """Display all products in a formatted table."""
        clear_screen()
        print_header("PRODUCT LIST")

        try:
            products = self.product_service.get_all_products()

            if not products:
                print("\nNo products found.")
                input("Press Enter to continue...")
                return

            headers: List[str] = ["ID", "Code", "Name", "Unit", "Price"]
            rows: List[List[str]] = [
                [
                    str(p.id),
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
            self.logger.error(f"Error in list_products: {str(e)}")
            input("Press Enter to continue...")

    def add_product(self) -> None:
        """Add a new product."""
        clear_screen()
        print_header("ADD NEW PRODUCT")

        try:
            code: str = input("\nProduct Code (8 digits): ").strip()
            name: str = input("Product Name: ").strip()
            unit: str = input("Unit of Measurement: ").strip()

            try:
                price: float = float(input("Price: "))
            except ValueError:
                print("❌ Invalid price format")
                input("Press Enter to continue...")
                return

            product = self.product_service.create_product(
                code=code,
                name=name,
                unit=unit,
                price=price,
                admin_id=self.admin_id
            )

            print(f"\n✓ Product created successfully!")
            print(f"  Code: {product.code}")
            print(f"  Name: {product.name}")
            print(f"  Unit: {product.unit}")
            print(f"  Price: {format_currency(float(product.price))}")

            if ask_continue("\nAdd another product? [Y/N]: "):
                self.add_product()

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Product creation failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in add_product: {str(e)}")
            input("Press Enter to continue...")

    def update_product(self) -> None:
        """Update an existing product."""
        clear_screen()
        print_header("UPDATE PRODUCT")

        try:
            # List products first
            products = self.product_service.get_all_products()
            if not products:
                print("\nNo products to update.")
                input("Press Enter to continue...")
                return

            try:
                product_id: int = int(input("\nEnter Product ID to update: "))
            except ValueError:
                print("❌ Invalid product ID")
                input("Press Enter to continue...")
                return

            product = self.product_service.get_product_by_id(product_id)

            print(f"\nCurrent Product:")
            print(f"  Code: {product.code}")
            print(f"  Name: {product.name}")
            print(f"  Unit: {product.unit}")
            print(f"  Price: {format_currency(float(product.price))}")

            print("\nEnter new values (leave blank to keep current):")

            updates: dict = {}

            new_code: str = input("New Code: ").strip()
            if new_code:
                updates["code"] = new_code

            new_name: str = input("New Name: ").strip()
            if new_name:
                updates["name"] = new_name

            new_unit: str = input("New Unit: ").strip()
            if new_unit:
                updates["unit"] = new_unit

            new_price: str = input("New Price: ").strip()
            if new_price:
                try:
                    updates["price"] = float(new_price)
                except ValueError:
                    print("❌ Invalid price format")
                    input("Press Enter to continue...")
                    return

            if not updates:
                print("\nNo changes made.")
                input("Press Enter to continue...")
                return

            updated_product = self.product_service.update_product(
                product_id=product_id,
                admin_id=self.admin_id,
                **updates
            )

            print(f"\n✓ Product updated successfully!")
            print(f"  Code: {updated_product.code}")
            print(f"  Name: {updated_product.name}")
            print(f"  Unit: {updated_product.unit}")
            print(f"  Price: {format_currency(float(updated_product.price))}")

            input("Press Enter to continue...")

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Product update failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in update_product: {str(e)}")
            input("Press Enter to continue...")

    def delete_product(self) -> None:
        """Delete a product."""
        clear_screen()
        print_header("DELETE PRODUCT")

        try:
            # List products first
            products = self.product_service.get_all_products()
            if not products:
                print("\nNo products to delete.")
                input("Press Enter to continue...")
                return

            try:
                product_id: int = int(input("\nEnter Product ID to delete: "))
            except ValueError:
                print("❌ Invalid product ID")
                input("Press Enter to continue...")
                return

            product = self.product_service.get_product_by_id(product_id)

            print(f"\nProduct to delete:")
            print(f"  Code: {product.code}")
            print(f"  Name: {product.name}")
            print(f"  Unit: {product.unit}")
            print(f"  Price: {format_currency(float(product.price))}")

            if ask_continue("\nAre you sure you want to delete this product? [Y/N]: "):
                self.product_service.delete_product(product_id, self.admin_id)
                print("\n✓ Product deleted successfully!")
                self.logger.info(f"Product {product_id} deleted by admin {self.admin_id}")

            input("Press Enter to continue...")

        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            self.logger.warning(f"Product deletion failed: {str(e)}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Error in delete_product: {str(e)}")
            input("Press Enter to continue...")

    def search_product(self) -> None:
        """Search for products by name."""
        clear_screen()
        print_header("SEARCH PRODUCTS")

        try:
            search_term: str = input("\nEnter product name to search: ").strip()

            if not search_term:
                print("❌ Search term cannot be empty")
                input("Press Enter to continue...")
                return

            products = self.product_service.search_products_by_name(search_term)

            if not products:
                print(f"\nNo products found matching '{search_term}'")
                input("Press Enter to continue...")
                return

            headers: List[str] = ["ID", "Code", "Name", "Unit", "Price"]
            rows: List[List[str]] = [
                [
                    str(p.id),
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
            print(f"\n❌ Error: {str(e)}")
            self.logger.error(f"Error in search_product: {str(e)}")
            input("Press Enter to continue...")
