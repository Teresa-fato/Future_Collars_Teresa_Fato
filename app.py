"""
Inventory Manager — Flask Web Application
Frontend with spectre.css for accounting and warehouse management.

Usage:
    pip install flask
    python app.py
"""

import os
from ast import literal_eval
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "inventory_manager_secret_key"

# ── File Paths ────────────────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BALANCE_FILE = os.path.join(DATA_DIR, "balance.txt")
WAREHOUSE_FILE = os.path.join(DATA_DIR, "warehouse.txt")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")


# ── File I/O ──────────────────────────────────────────────────────────


def load_balance():
    """Load account balance from file."""
    try:
        with open(BALANCE_FILE, "r") as f:
            value = literal_eval(f.read().strip())
            if isinstance(value, (int, float)):
                return float(value)
    except (FileNotFoundError, ValueError, SyntaxError, OSError):
        pass
    return 0.0


def save_balance(balance):
    """Save account balance to file."""
    with open(BALANCE_FILE, "w") as f:
        f.write(repr(balance))


def load_warehouse():
    """Load warehouse inventory from file."""
    try:
        with open(WAREHOUSE_FILE, "r") as f:
            data = literal_eval(f.read().strip())
            if isinstance(data, dict):
                return data
    except (FileNotFoundError, ValueError, SyntaxError, OSError):
        pass
    return {}


def save_warehouse(warehouse):
    """Save warehouse inventory to file."""
    with open(WAREHOUSE_FILE, "w") as f:
        f.write(repr(warehouse))


def load_history():
    """Load operation history from file."""
    try:
        with open(HISTORY_FILE, "r") as f:
            data = literal_eval(f.read().strip())
            if isinstance(data, list):
                return data
    except (FileNotFoundError, ValueError, SyntaxError, OSError):
        pass
    return []


def save_history(history):
    """Save operation history to file."""
    with open(HISTORY_FILE, "w") as f:
        f.write(repr(history))


def add_to_history(entry):
    """Append an entry to the history and save."""
    history = load_history()
    history.append(entry)
    save_history(history)


# ── Routes ────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Main page — display current stock and account balance."""
    balance = load_balance()
    warehouse = load_warehouse()
    return render_template("index.html", balance=balance, warehouse=warehouse)


# ── Purchase ──────────────────────────────────────────────────────────


@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    """Purchase form — buy products and add to warehouse."""
    if request.method == "POST":
        name = request.form.get("product_name", "").strip()
        price_str = request.form.get("unit_price", "").strip()
        quantity_str = request.form.get("quantity", "").strip()

        # Validation
        if not name:
            flash("Product name is required.", "error")
            return redirect(url_for("purchase"))

        try:
            price = float(price_str)
        except (ValueError, TypeError):
            flash("Unit price must be a valid number.", "error")
            return redirect(url_for("purchase"))

        try:
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            flash("Quantity must be a valid whole number.", "error")
            return redirect(url_for("purchase"))

        if price <= 0:
            flash("Unit price must be positive.", "error")
            return redirect(url_for("purchase"))

        if quantity <= 0:
            flash("Quantity must be positive.", "error")
            return redirect(url_for("purchase"))

        total = price * quantity
        balance = load_balance()

        if balance - total < 0:
            flash(f"Insufficient funds. Cost: {total:.2f}, Balance: {balance:.2f}", "error")
            return redirect(url_for("purchase"))

        # Execute purchase
        balance -= total
        save_balance(balance)

        warehouse = load_warehouse()
        if name in warehouse:
            warehouse[name]["quantity"] += quantity
            warehouse[name]["price"] = price
        else:
            warehouse[name] = {"price": price, "quantity": quantity}
        save_warehouse(warehouse)

        add_to_history(f"Purchase: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {balance:.2f}")
        flash(f"Purchased {quantity}x '{name}' for {total:.2f}.", "success")
        return redirect(url_for("index"))

    return render_template("purchase.html")


# ── Sale ──────────────────────────────────────────────────────────────


@app.route("/sale", methods=["GET", "POST"])
def sale():
    """Sale form — sell products from warehouse."""
    if request.method == "POST":
        name = request.form.get("product_name", "").strip()
        price_str = request.form.get("unit_price", "").strip()
        quantity_str = request.form.get("quantity", "").strip()

        # Validation
        if not name:
            flash("Product name is required.", "error")
            return redirect(url_for("sale"))

        try:
            price = float(price_str)
        except (ValueError, TypeError):
            flash("Unit price must be a valid number.", "error")
            return redirect(url_for("sale"))

        try:
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            flash("Quantity must be a valid whole number.", "error")
            return redirect(url_for("sale"))

        if price <= 0:
            flash("Unit price must be positive.", "error")
            return redirect(url_for("sale"))

        if quantity <= 0:
            flash("Quantity must be positive.", "error")
            return redirect(url_for("sale"))

        warehouse = load_warehouse()

        if name not in warehouse:
            flash(f"'{name}' not found in warehouse.", "error")
            return redirect(url_for("sale"))

        if warehouse[name]["quantity"] < quantity:
            flash(f"Insufficient stock. Only {warehouse[name]['quantity']} unit(s) of '{name}' available.", "error")
            return redirect(url_for("sale"))

        # Execute sale
        total = price * quantity
        balance = load_balance()
        balance += total
        save_balance(balance)

        warehouse[name]["quantity"] -= quantity
        if warehouse[name]["quantity"] == 0:
            del warehouse[name]
        save_warehouse(warehouse)

        add_to_history(f"Sale: {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {balance:.2f}")
        flash(f"Sold {quantity}x '{name}' for {total:.2f}.", "success")
        return redirect(url_for("index"))

    return render_template("sale.html")


# ── Balance ───────────────────────────────────────────────────────────


@app.route("/balance", methods=["GET", "POST"])
def balance():
    """Balance change form — add or subtract from account."""
    if request.method == "POST":
        operation = request.form.get("operation", "").strip()
        amount_str = request.form.get("amount", "").strip()

        if operation not in ("add", "subtract"):
            flash("Please select a valid operation (add or subtract).", "error")
            return redirect(url_for("balance"))

        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            flash("Amount must be a valid number.", "error")
            return redirect(url_for("balance"))

        if amount <= 0:
            flash("Amount must be positive.", "error")
            return redirect(url_for("balance"))

        current = load_balance()

        if operation == "add":
            current += amount
            action = "added to"
        else:
            current -= amount
            action = "subtracted from"

        save_balance(current)
        add_to_history(f"Balance: {amount:.2f} {action} account. New balance: {current:.2f}")
        flash(f"{amount:.2f} {action} account. New balance: {current:.2f}", "success")
        return redirect(url_for("index"))

    return render_template("balance.html")


# ── History ───────────────────────────────────────────────────────────


@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History page — display operation history with optional range."""
    all_history = load_history()
    total = len(all_history)
    filtered = False
    error_msg = None

    if line_from is not None and line_to is not None:
        # Clamp to valid range
        actual_from = max(0, line_from)
        actual_to = min(total, line_to + 1)

        if actual_from != line_from or actual_to != line_to + 1:
            error_msg = f"Range adjusted to [{actual_from}–{actual_to - 1}] (original: [{line_from}–{line_to}])."

        if actual_from >= actual_to:
            display_history = []
            error_msg = f"Invalid range [{line_from}–{line_to}]. No operations to display."
        else:
            display_history = list(enumerate(all_history[actual_from:actual_to], start=actual_from))
            filtered = True
    else:
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
    app.run(debug=True, port=5000)
