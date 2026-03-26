"""
Inventory Manager with Manager Class & Decorators
— Extends the accounting system with a Manager class.
— Commands (sale, purchase, balance, etc.) are registered via @manager.assign decorator.
— File persistence for balance, warehouse, and history.

Usage:
    python inventory_manager_decorators.py
"""

import os
import functools
from ast import literal_eval
from datetime import datetime


# ── File Paths ────────────────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BALANCE_FILE = os.path.join(DATA_DIR, "balance.txt")
WAREHOUSE_FILE = os.path.join(DATA_DIR, "warehouse.txt")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")


# ── Logging Decorator ─────────────────────────────────────────────────


def log_action(func):
    """Decorator that logs command execution with a timestamp to history."""

    @functools.wraps(func)
    def wrapper(mgr, *args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command_name = func.__name__.replace("handle_", "")
        result = func(mgr, *args, **kwargs)
        mgr.history.append(f"[{timestamp}] Command: {command_name}")
        return result

    return wrapper


# ── Input Helpers ─────────────────────────────────────────────────────


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


# ── Manager Class ─────────────────────────────────────────────────────


class Manager:
    """Manages accounting operations using decorator-registered commands.

    Usage:
        manager = Manager()

        @manager.assign("sale")
        def handle_sale(mgr):
            ...

        manager.execute("sale")  # calls handle_sale(manager)
    """

    def __init__(self):
        self._commands = {}  # {command_name: function}
        self.account_balance = 0.0
        self.warehouse = {}   # {product_name: {"price": float, "quantity": int}}
        self.history = []     # list of operation strings
        self.running = True   # controls main loop

        # Load saved state
        self._load_state()

    # ── Assign Decorator ──────────────────────────────────────────────

    def assign(self, command_name):
        """Decorator that registers a function as a named command.

        Usage:
            @manager.assign("balance")
            def handle_balance(mgr):
                ...
        """

        def decorator(func):
            self._commands[command_name] = func
            return func

        return decorator

    # ── Execute Command ───────────────────────────────────────────────

    def execute(self, command_name):
        """Execute a registered command by name.

        Args:
            command_name: The name of the command to execute.

        Returns:
            True if command was found and executed, False otherwise.
        """
        if command_name in self._commands:
            self._commands[command_name](self)
            return True
        else:
            print(f"  [!] Unknown command: '{command_name}'. Please try again.")
            return False

    # ── List Commands ─────────────────────────────────────────────────

    def list_commands(self):
        """Return a list of all registered command names."""
        return list(self._commands.keys())

    # ── File I/O ──────────────────────────────────────────────────────

    def _load_state(self):
        """Load account balance, warehouse, and history from files."""
        print("  Loading saved data...\n")

        # Load balance
        try:
            with open(BALANCE_FILE, "r") as f:
                value = literal_eval(f.read().strip())
                if isinstance(value, (int, float)):
                    self.account_balance = float(value)
                    print(f"  ✓ Balance loaded: {self.account_balance:.2f}")
        except FileNotFoundError:
            print("  No saved balance found. Starting with 0.00.")
        except (ValueError, SyntaxError, OSError):
            print("  [!] Balance file error. Starting with 0.00.")

        # Load warehouse
        try:
            with open(WAREHOUSE_FILE, "r") as f:
                data = literal_eval(f.read().strip())
                if isinstance(data, dict):
                    self.warehouse = data
                    print(f"  ✓ Warehouse loaded: {len(self.warehouse)} product(s)")
        except FileNotFoundError:
            print("  No saved warehouse found. Starting empty.")
        except (ValueError, SyntaxError, OSError):
            print("  [!] Warehouse file error. Starting empty.")

        # Load history
        try:
            with open(HISTORY_FILE, "r") as f:
                data = literal_eval(f.read().strip())
                if isinstance(data, list):
                    self.history = data
                    print(f"  ✓ History loaded: {len(self.history)} operation(s)")
        except FileNotFoundError:
            print("  No saved history found. Starting empty.")
        except (ValueError, SyntaxError, OSError):
            print("  [!] History file error. Starting empty.")

    def save_state(self):
        """Save account balance, warehouse, and history to files."""
        errors = []

        try:
            with open(BALANCE_FILE, "w") as f:
                f.write(repr(self.account_balance))
        except OSError as e:
            errors.append(f"Balance: {e}")

        try:
            with open(WAREHOUSE_FILE, "w") as f:
                f.write(repr(self.warehouse))
        except OSError as e:
            errors.append(f"Warehouse: {e}")

        try:
            with open(HISTORY_FILE, "w") as f:
                f.write(repr(self.history))
        except OSError as e:
            errors.append(f"History: {e}")

        if errors:
            print("  [!] Errors saving data:")
            for err in errors:
                print(f"      - {err}")
        else:
            print("  ✓ All data saved successfully.")


# ── Create Manager Instance ──────────────────────────────────────────

manager = Manager()


# ── Register Commands via Decorators ──────────────────────────────────


@manager.assign("balance")
@log_action
def handle_balance(mgr):
    """Add or subtract an amount from the account balance."""
    amount = get_float("  Enter amount (positive to add, negative to subtract): ")
    mgr.account_balance += amount
    action = "added to" if amount >= 0 else "subtracted from"
    mgr.history.append(f"Balance: {abs(amount):.2f} {action} account. New balance: {mgr.account_balance:.2f}")
    print(f"  ✓ {abs(amount):.2f} {action} account. Current balance: {mgr.account_balance:.2f}")


@manager.assign("sale")
@log_action
def handle_sale(mgr):
    """Record a sale — remove product from warehouse, credit the account."""
    name = input("  Product name: ").strip()
    if not name:
        print("  [!] Product name cannot be empty.")
        return

    price = get_float("  Sale price per unit: ")
    quantity = get_int("  Quantity sold: ")

    if quantity <= 0:
        print("  [!] Quantity must be positive.")
        return

    if name not in mgr.warehouse:
        print(f"  [!] '{name}' not found in warehouse. Cannot complete sale.")
        return

    if mgr.warehouse[name]["quantity"] < quantity:
        print(f"  [!] Insufficient stock. Only {mgr.warehouse[name]['quantity']} unit(s) of '{name}' available.")
        return

    total = price * quantity
    mgr.account_balance += total
    mgr.warehouse[name]["quantity"] -= quantity

    if mgr.warehouse[name]["quantity"] == 0:
        del mgr.warehouse[name]

    mgr.history.append(f"Sale: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {mgr.account_balance:.2f}")
    print(f"  ✓ Sold {quantity}x '{name}' for {total:.2f}. Current balance: {mgr.account_balance:.2f}")


@manager.assign("purchase")
@log_action
def handle_purchase(mgr):
    """Record a purchase — add product to warehouse, debit the account."""
    name = input("  Product name: ").strip()
    if not name:
        print("  [!] Product name cannot be empty.")
        return

    price = get_float("  Purchase price per unit: ")
    quantity = get_int("  Quantity purchased: ")

    if quantity <= 0:
        print("  [!] Quantity must be positive.")
        return

    total = price * quantity

    if mgr.account_balance - total < 0:
        print(f"  [!] Insufficient funds. Cost: {total:.2f}, Balance: {mgr.account_balance:.2f}")
        return

    mgr.account_balance -= total

    if name in mgr.warehouse:
        mgr.warehouse[name]["quantity"] += quantity
        mgr.warehouse[name]["price"] = price
    else:
        mgr.warehouse[name] = {"price": price, "quantity": quantity}

    mgr.history.append(f"Purchase: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {mgr.account_balance:.2f}")
    print(f"  ✓ Purchased {quantity}x '{name}' for {total:.2f}. Current balance: {mgr.account_balance:.2f}")


@manager.assign("account")
@log_action
def handle_account(mgr):
    """Display the current account balance."""
    print(f"\n  Current account balance: {mgr.account_balance:.2f}")


@manager.assign("list")
@log_action
def handle_list(mgr):
    """Display the full warehouse inventory."""
    if not mgr.warehouse:
        print("\n  Warehouse is empty.")
        return

    print(f"\n  {'Product':<20} {'Price':>10} {'Quantity':>10}")
    print("  " + "-" * 42)
    for name, info in mgr.warehouse.items():
        print(f"  {name:<20} {info['price']:>10.2f} {info['quantity']:>10}")
    print("  " + "-" * 42)
    print(f"  Total unique products: {len(mgr.warehouse)}")


@manager.assign("warehouse")
@log_action
def handle_warehouse(mgr):
    """Look up a specific product in the warehouse."""
    name = input("  Product name to look up: ").strip()
    if not name:
        print("  [!] Product name cannot be empty.")
        return

    if name in mgr.warehouse:
        info = mgr.warehouse[name]
        print(f"\n  Product : {name}")
        print(f"  Price   : {info['price']:.2f}")
        print(f"  Quantity: {info['quantity']}")
    else:
        print(f"  '{name}' is not in the warehouse.")


@manager.assign("review")
@log_action
def handle_review(mgr):
    """Display recorded operations within an optional index range."""
    if not mgr.history:
        print("\n  No operations recorded yet.")
        return

    from_str = input(f"  From index (0–{len(mgr.history) - 1}, or Enter for all): ").strip()
    to_str = input(f"  To index   (0–{len(mgr.history) - 1}, or Enter for all): ").strip()

    if from_str == "" and to_str == "":
        start, end = 0, len(mgr.history)
    else:
        try:
            start = int(from_str) if from_str else 0
            end = int(to_str) + 1 if to_str else len(mgr.history)
        except ValueError:
            print("  [!] Indices must be whole numbers.")
            return

        if start < 0:
            print(f"  [!] 'from' index adjusted from {start} to 0.")
            start = 0
        if end > len(mgr.history):
            print(f"  [!] 'to' index adjusted from {end - 1} to {len(mgr.history) - 1}.")
            end = len(mgr.history)
        if start >= end:
            print("  [!] 'from' must be less than 'to'. No operations to display.")
            return

    print(f"\n  Operations [{start}–{end - 1}]:")
    print("  " + "-" * 60)
    for i in range(start, end):
        print(f"  [{i}] {mgr.history[i]}")
    print("  " + "-" * 60)


@manager.assign("end")
def handle_end(mgr):
    """Save state and terminate the program."""
    print("\n  Saving data...")
    mgr.save_state()
    mgr.running = False
    print("  Goodbye!\n")


# ── Display Menu ──────────────────────────────────────────────────────


def display_commands():
    """Display available commands."""
    print("\n" + "=" * 45)
    print("  INVENTORY MANAGER (Decorators Edition)")
    print("=" * 45)
    descriptions = {
        "balance": "Add or subtract from account",
        "sale": "Record a product sale",
        "purchase": "Record a product purchase",
        "account": "View current account balance",
        "list": "View full warehouse inventory",
        "warehouse": "Look up a specific product",
        "review": "Review operation history",
        "end": "Save & exit the program",
    }
    for cmd in manager.list_commands():
        desc = descriptions.get(cmd, "")
        print(f"  {cmd:<12} — {desc}")
    print("=" * 45)


# ── Main ──────────────────────────────────────────────────────────────


def main():
    """Main application loop using Manager.execute()."""
    print("\n  Welcome to Inventory Manager (Decorators Edition)!")

    while manager.running:
        display_commands()
        command = input("\n  Enter command: ").strip().lower()
        manager.execute(command)


if __name__ == "__main__":
    main()
