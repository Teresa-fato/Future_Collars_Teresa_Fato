"""
Inventory Manager — A CLI-based inventory and account management system.
Supports sales, purchases, balance adjustments, warehouse tracking, and operation history.
"""


def display_commands():
    """Display available commands to the user."""
    print("\n" + "=" * 45)
    print("  INVENTORY MANAGER — Available Commands")
    print("=" * 45)
    commands = [
        ("balance", "Add or subtract from account"),
        ("sale", "Record a product sale"),
        ("purchase", "Record a product purchase"),
        ("account", "View current account balance"),
        ("list", "View full warehouse inventory"),
        ("warehouse", "Look up a specific product"),
        ("review", "Review operation history"),
        ("end", "Exit the program"),
    ]
    for cmd, desc in commands:
        print(f"  {cmd:<12} — {desc}")
    print("=" * 45)


def get_float(prompt):
    """Prompt for a float value with validation."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  [!] Please enter a valid number.")


def get_int(prompt):
    """Prompt for an integer value with validation."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  [!] Please enter a valid whole number.")


def handle_balance(account_balance, history):
    """Add or subtract an amount from the account balance."""
    amount = get_float("  Enter amount (positive to add, negative to subtract): ")
    account_balance += amount
    action = "added to" if amount >= 0 else "subtracted from"
    history.append(f"Balance: {abs(amount):.2f} {action} account. New balance: {account_balance:.2f}")
    print(f"  ✓ {abs(amount):.2f} {action} account. Current balance: {account_balance:.2f}")
    return account_balance


def handle_sale(account_balance, warehouse, history):
    """Record a sale — remove product from warehouse, credit the account."""
    name = input("  Product name: ").strip()
    if not name:
        print("  [!] Product name cannot be empty.")
        return account_balance

    price = get_float("  Sale price per unit: ")
    quantity = get_int("  Quantity sold: ")

    if quantity <= 0:
        print("  [!] Quantity must be positive.")
        return account_balance

    # Check warehouse stock
    if name not in warehouse:
        print(f"  [!] '{name}' not found in warehouse. Cannot complete sale.")
        return account_balance

    if warehouse[name]["quantity"] < quantity:
        print(f"  [!] Insufficient stock. Only {warehouse[name]['quantity']} unit(s) of '{name}' available.")
        return account_balance

    total = price * quantity
    account_balance += total
    warehouse[name]["quantity"] -= quantity

    # Remove product entry if quantity reaches zero
    if warehouse[name]["quantity"] == 0:
        del warehouse[name]

    history.append(f"Sale: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {account_balance:.2f}")
    print(f"  ✓ Sold {quantity}x '{name}' for {total:.2f}. Current balance: {account_balance:.2f}")
    return account_balance


def handle_purchase(account_balance, warehouse, history):
    """Record a purchase — add product to warehouse, debit the account."""
    name = input("  Product name: ").strip()
    if not name:
        print("  [!] Product name cannot be empty.")
        return account_balance

    price = get_float("  Purchase price per unit: ")
    quantity = get_int("  Quantity purchased: ")

    if quantity <= 0:
        print("  [!] Quantity must be positive.")
        return account_balance

    total = price * quantity

    # Ensure account won't go negative
    if account_balance - total < 0:
        print(f"  [!] Insufficient funds. Cost: {total:.2f}, Balance: {account_balance:.2f}")
        return account_balance

    account_balance -= total

    if name in warehouse:
        warehouse[name]["quantity"] += quantity
        warehouse[name]["price"] = price  # Update to latest purchase price
    else:
        warehouse[name] = {"price": price, "quantity": quantity}

    history.append(f"Purchase: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {account_balance:.2f}")
    print(f"  ✓ Purchased {quantity}x '{name}' for {total:.2f}. Current balance: {account_balance:.2f}")
    return account_balance


def handle_account(account_balance):
    """Display the current account balance."""
    print(f"\n  Current account balance: {account_balance:.2f}")


def handle_list(warehouse):
    """Display the full warehouse inventory."""
    if not warehouse:
        print("\n  Warehouse is empty.")
        return

    print(f"\n  {'Product':<20} {'Price':>10} {'Quantity':>10}")
    print("  " + "-" * 42)
    for name, info in warehouse.items():
        print(f"  {name:<20} {info['price']:>10.2f} {info['quantity']:>10}")
    print("  " + "-" * 42)
    print(f"  Total unique products: {len(warehouse)}")


def handle_warehouse(warehouse):
    """Look up a specific product in the warehouse."""
    name = input("  Product name to look up: ").strip()
    if not name:
        print("  [!] Product name cannot be empty.")
        return

    if name in warehouse:
        info = warehouse[name]
        print(f"\n  Product : {name}")
        print(f"  Price   : {info['price']:.2f}")
        print(f"  Quantity: {info['quantity']}")
    else:
        print(f"  '{name}' is not in the warehouse.")


def handle_review(history):
    """Display recorded operations within an optional index range."""
    if not history:
        print("\n  No operations recorded yet.")
        return

    from_str = input(f"  From index (0–{len(history) - 1}, or Enter for all): ").strip()
    to_str = input(f"  To index   (0–{len(history) - 1}, or Enter for all): ").strip()

    # Default to full range if empty
    if from_str == "" and to_str == "":
        start, end = 0, len(history)
    else:
        try:
            start = int(from_str) if from_str else 0
            end = int(to_str) + 1 if to_str else len(history)
        except ValueError:
            print("  [!] Indices must be whole numbers.")
            return

        # Clamp to valid range
        if start < 0:
            print(f"  [!] 'from' index adjusted from {start} to 0.")
            start = 0
        if end > len(history):
            print(f"  [!] 'to' index adjusted from {end - 1} to {len(history) - 1}.")
            end = len(history)
        if start >= end:
            print("  [!] 'from' must be less than 'to'. No operations to display.")
            return

    print(f"\n  Operations [{start}–{end - 1}]:")
    print("  " + "-" * 50)
    for i in range(start, end):
        print(f"  [{i}] {history[i]}")
    print("  " + "-" * 50)


def main():
    """Main application loop."""
    account_balance = 0.0
    warehouse = {}   # {product_name: {"price": float, "quantity": int}}
    history = []     # List of operation descriptions

    print("\n  Welcome to Inventory Manager!")

    while True:
        display_commands()
        command = input("\n  Enter command: ").strip().lower()

        if command == "balance":
            account_balance = handle_balance(account_balance, history)
        elif command == "sale":
            account_balance = handle_sale(account_balance, warehouse, history)
        elif command == "purchase":
            account_balance = handle_purchase(account_balance, warehouse, history)
        elif command == "account":
            handle_account(account_balance)
        elif command == "list":
            handle_list(warehouse)
        elif command == "warehouse":
            handle_warehouse(warehouse)
        elif command == "review":
            handle_review(history)
        elif command == "end":
            print("\n  Goodbye!\n")
            break
        else:
            print(f"  [!] Unknown command: '{command}'. Please try again.")


if __name__ == "__main__":
    main()
