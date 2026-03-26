"""
Inventory Manager — Flask Backend
Handles routes, form submissions, data management, and file I/O.
Uses templates_backend/ for HTML templates.

Usage:
    pip install flask
    python app_backend.py
"""

import os
from ast import literal_eval
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder="templates_backend")
app.secret_key = "inventory_backend_secret_key"

# ── File Paths ────────────────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BALANCE_FILE = os.path.join(DATA_DIR, "data_balance.txt")
WAREHOUSE_FILE = os.path.join(DATA_DIR, "data_warehouse.txt")
HISTORY_FILE = os.path.join(DATA_DIR, "data_history.txt")


# ── File I/O — Read ──────────────────────────────────────────────────


def load_balance():
    """Load account balance from file.

    Returns:
        float: Account balance, or 0.0 if file is missing/corrupted.
    """
    try:
        with open(BALANCE_FILE, "r") as f:
            value = literal_eval(f.read().strip())
            if isinstance(value, (int, float)):
                return float(value)
    except FileNotFoundError:
        pass
    except (ValueError, SyntaxError):
        print(f"  [!] Warning: {BALANCE_FILE} is corrupted. Using default.")
    except OSError as e:
        print(f"  [!] Warning: Could not read {BALANCE_FILE}: {e}")
    return 0.0


def load_warehouse():
    """Load warehouse inventory from file.

    Returns:
        dict: Warehouse data {name: {"price": float, "quantity": int}},
              or empty dict if file is missing/corrupted.
    """
    try:
        with open(WAREHOUSE_FILE, "r") as f:
            data = literal_eval(f.read().strip())
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        pass
    except (ValueError, SyntaxError):
        print(f"  [!] Warning: {WAREHOUSE_FILE} is corrupted. Using default.")
    except OSError as e:
        print(f"  [!] Warning: Could not read {WAREHOUSE_FILE}: {e}")
    return {}


def load_history():
    """Load operation history from file.

    Returns:
        list: List of operation strings, or empty list if file is missing/corrupted.
    """
    try:
        with open(HISTORY_FILE, "r") as f:
            data = literal_eval(f.read().strip())
            if isinstance(data, list):
                return data
    except FileNotFoundError:
        pass
    except (ValueError, SyntaxError):
        print(f"  [!] Warning: {HISTORY_FILE} is corrupted. Using default.")
    except OSError as e:
        print(f"  [!] Warning: Could not read {HISTORY_FILE}: {e}")
    return []


# ── File I/O — Write ─────────────────────────────────────────────────


def save_balance(balance):
    """Save account balance to file.

    Args:
        balance (float): The balance to save.
    """
    try:
        with open(BALANCE_FILE, "w") as f:
            f.write(repr(balance))
    except OSError as e:
        print(f"  [!] Error saving balance: {e}")


def save_warehouse(warehouse):
    """Save warehouse inventory to file.

    Args:
        warehouse (dict): The warehouse data to save.
    """
    try:
        with open(WAREHOUSE_FILE, "w") as f:
            f.write(repr(warehouse))
    except OSError as e:
        print(f"  [!] Error saving warehouse: {e}")


def save_history(history):
    """Save operation history to file.

    Args:
        history (list): The history list to save.
    """
    try:
        with open(HISTORY_FILE, "w") as f:
            f.write(repr(history))
    except OSError as e:
        print(f"  [!] Error saving history: {e}")


def add_to_history(entry):
    """Append an entry to the history and save to file.

    Args:
        entry (str): The operation description to log.
    """
    history = load_history()
    history.append(entry)
    save_history(history)


# ── Validation Helpers ────────────────────────────────────────────────


def validate_product_form(form):
    """Validate product form fields (used by purchase and sale).

    Args:
        form: Flask request.form object.

    Returns:
        tuple: (name, price, quantity) if valid, or (None, None, None) + flash on error.
    """
    name = form.get("product_name", "").strip()
    price_str = form.get("unit_price", "").strip()
    quantity_str = form.get("quantity", "").strip()

    if not name:
        flash("Product name is required.", "error")
        return None, None, None

    try:
        price = float(price_str)
    except (ValueError, TypeError):
        flash("Unit price must be a valid number.", "error")
        return None, None, None

    try:
        quantity = int(quantity_str)
    except (ValueError, TypeError):
        flash("Quantity must be a valid whole number.", "error")
        return None, None, None

    if price <= 0:
        flash("Unit price must be positive.", "error")
        return None, None, None

    if quantity <= 0:
        flash("Quantity must be positive.", "error")
        return None, None, None

    return name, price, quantity


# ── Routes — Main Page ────────────────────────────────────────────────


@app.route("/")
def index():
    """Main page — display current stock level and account balance.

    Reads balance and warehouse from files and renders the dashboard.
    """
    balance = load_balance()
    warehouse = load_warehouse()
    return render_template("index.html", balance=balance, warehouse=warehouse)


# ── Routes — Purchase ─────────────────────────────────────────────────


@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    """Purchase route — buy products and add to warehouse.

    GET:  Display purchase form.
    POST: Validate input, check funds, update warehouse + balance + history.
          Redirect to index on success, back to form on error.
    """
    if request.method == "POST":
        name, price, quantity = validate_product_form(request.form)
        if name is None:
            return redirect(url_for("purchase"))

        total = price * quantity
        balance = load_balance()

        # Business rule: account balance cannot go negative after purchase
        if balance - total < 0:
            flash(
                f"Insufficient funds. Cost: {total:.2f}, Available: {balance:.2f}",
                "error",
            )
            return redirect(url_for("purchase"))

        # Update balance
        balance -= total
        save_balance(balance)

        # Update warehouse
        warehouse = load_warehouse()
        if name in warehouse:
            warehouse[name]["quantity"] += quantity
            warehouse[name]["price"] = price
        else:
            warehouse[name] = {"price": price, "quantity": quantity}
        save_warehouse(warehouse)

        # Log to history
        add_to_history(
            f"Purchase: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. "
            f"Balance: {balance:.2f}"
        )

        flash(f"Purchased {quantity}x '{name}' for {total:.2f}.", "success")
        return redirect(url_for("index"))

    return render_template("purchase.html")


# ── Routes — Sale ─────────────────────────────────────────────────────


@app.route("/sale", methods=["GET", "POST"])
def sale():
    """Sale route — sell products from warehouse.

    GET:  Display sale form.
    POST: Validate input, check stock, update warehouse + balance + history.
          Redirect to index on success, back to form on error.
    """
    if request.method == "POST":
        name, price, quantity = validate_product_form(request.form)
        if name is None:
            return redirect(url_for("sale"))

        warehouse = load_warehouse()

        # Business rule: product must exist in warehouse
        if name not in warehouse:
            flash(f"'{name}' not found in warehouse.", "error")
            return redirect(url_for("sale"))

        # Business rule: sufficient stock required
        if warehouse[name]["quantity"] < quantity:
            flash(
                f"Insufficient stock. Only {warehouse[name]['quantity']} "
                f"unit(s) of '{name}' available.",
                "error",
            )
            return redirect(url_for("sale"))

        # Update balance
        total = price * quantity
        balance = load_balance()
        balance += total
        save_balance(balance)

        # Update warehouse
        warehouse[name]["quantity"] -= quantity
        if warehouse[name]["quantity"] == 0:
            del warehouse[name]
        save_warehouse(warehouse)

        # Log to history
        add_to_history(
            f"Sale: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. "
            f"Balance: {balance:.2f}"
        )

        flash(f"Sold {quantity}x '{name}' for {total:.2f}.", "success")
        return redirect(url_for("index"))

    return render_template("sale.html")


# ── Routes — Balance ──────────────────────────────────────────────────


@app.route("/balance", methods=["GET", "POST"])
def balance():
    """Balance change route — add or subtract from account.

    GET:  Display balance form with add/subtract radio buttons.
    POST: Validate input, update balance + history.
          Redirect to index on success, back to form on error.
    """
    if request.method == "POST":
        operation = request.form.get("operation", "").strip()
        amount_str = request.form.get("amount", "").strip()

        # Validate operation type
        if operation not in ("add", "subtract"):
            flash("Please select a valid operation (add or subtract).", "error")
            return redirect(url_for("balance"))

        # Validate amount
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            flash("Amount must be a valid number.", "error")
            return redirect(url_for("balance"))

        if amount <= 0:
            flash("Amount must be positive.", "error")
            return redirect(url_for("balance"))

        # Apply operation
        current = load_balance()

        if operation == "add":
            current += amount
            action = "added to"
        else:
            current -= amount
            action = "subtracted from"

        save_balance(current)

        # Log to history
        add_to_history(
            f"Balance: {amount:.2f} {action} account. New balance: {current:.2f}"
        )

        flash(f"{amount:.2f} {action} account. New balance: {current:.2f}", "success")
        return redirect(url_for("index"))

    return render_template("balance.html")


# ── Routes — History ──────────────────────────────────────────────────


@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History route — display operation history with optional range.

    URL patterns:
        /history/                     → display all history
        /history/<line_from>/<line_to>/ → display range [line_from, line_to]

    Handles out-of-range values by clamping to valid boundaries.
    """
    all_history = load_history()
    total = len(all_history)
    filtered = False
    error_msg = None

    if line_from is not None and line_to is not None:
        # Clamp indices to valid range
        actual_from = max(0, line_from)
        actual_to = min(total, line_to + 1)  # +1 because range is inclusive

        # Report if range was adjusted
        if actual_from != line_from or actual_to != line_to + 1:
            error_msg = (
                f"Range adjusted to [{actual_from}–{actual_to - 1}] "
                f"(requested: [{line_from}–{line_to}], total: {total})."
            )

        # Handle invalid range
        if actual_from >= actual_to:
            display_history = []
            error_msg = (
                f"Invalid range [{line_from}–{line_to}]. "
                f"No operations to display (total: {total})."
            )
        else:
            display_history = list(
                enumerate(all_history[actual_from:actual_to], start=actual_from)
            )
            filtered = True
    else:
        # No parameters — display all history
        display_history = list(enumerate(all_history))

    return render_template(
        "history.html",
        history=display_history,
        total=total,
        filtered=filtered,
        line_from=line_from,
        line_to=line_to,
        error_msg=error_msg,
    )


# ── Run ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5001)
