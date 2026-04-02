import os
from typing import List


def clear_screen() -> None:
    """Clear the terminal screen.
    
    Works on both Windows (cls) and Unix-like systems (clear).
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str) -> None:
    """Print a formatted header with borders.
    
    Args:
        title: The header title text.
    """
    width: int = 60
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def ask_continue(prompt: str = "Enter another? [Y/N]: ") -> bool:
    """Ask user if they want to continue an operation.
    
    Loops until valid input (Y or N) is received.
    
    Args:
        prompt: The prompt message to display.
    
    Returns:
        True if user enters Y, False if user enters N.
    """
    while True:
        answer: str = input(prompt).strip().upper()
        if answer in ['Y', 'YES']:
            return True
        elif answer in ['N', 'NO']:
            return False
        else:
            print("Invalid input. Please enter Y or N.")


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    """Print a formatted table with headers and rows.
    
    Automatically calculates column widths based on content.
    
    Args:
        headers: List of column header strings.
        rows: List of rows, each row is a list of strings.
    """
    if not headers or not rows:
        print("No data to display.")
        return

    # Calculate column widths
    col_widths: List[int] = [
        max(len(h), max(len(str(r[i])) for r in rows) if rows else 0)
        for i, h in enumerate(headers)
    ]

    # Print header
    header_row: str = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))

    # Print rows
    for row in rows:
        print(" | ".join(str(r).ljust(w) for r, w in zip(row, col_widths)))


def format_currency(value: float) -> str:
    """Format a value as currency (PHP).
    
    Args:
        value: The numeric value to format.
    
    Returns:
        Formatted currency string (e.g., "₱1,234.56").
    """
    return f"₱{value:,.2f}"


def format_decimal(value: float, decimals: int = 2) -> str:
    """Format a decimal number with specified precision.
    
    Args:
        value: The numeric value to format.
        decimals: Number of decimal places (default 2).
    
    Returns:
        Formatted decimal string.
    """
    return f"{value:.{decimals}f}"
