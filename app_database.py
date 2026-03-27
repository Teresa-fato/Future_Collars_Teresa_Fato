"""
Inventory Manager — Flask + SQLite (Flask-SQLAlchemy)
Separate from previous apps. Uses SQLite database for all persistence.

Usage:
    pip install flask flask-sqlalchemy
    python app_database.py

Opens on http://localhost:5002
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# ── App Configuration ─────────────────────────────────────────────────

app = Flask(__name__, template_folder="templates_database")
app.secret_key = "inventory-db-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ── Database Models ───────────────────────────────────────────────────


class Account(db.Model):
    """Stores the single account balance record."""
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<Account balance={self.balance:.2f}>"


class Product(db.Model):
    """Stores warehouse products with name, price, and quantity."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Product {self.name} price={self.price:.2f} qty={self.quantity}>"


class Transaction(db.Model):
    """Stores the history of all operations."""
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    operation = db.Column(db.String(50), nullable=False)  # purchase, sale, balance
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Transaction [{self.operation}] {self.description}>"


# ── Database Helpers ──────────────────────────────────────────────────


def get_account():
    """Get or create the single account record."""
    try:
        account = Account.query.first()
        if account is None:
            account = Account(balance=0.0)
            db.session.add(account)
            db.session.commit()
        return account
    except Exception as e:
        db.session.rollback()
        raise e


def log_transaction(operation, description):
    """Log an operation to the transaction history."""
    try:
        txn = Transaction(
            timestamp=datetime.now(),
            operation=operation,
            description=description,
        )
        db.session.add(txn)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


# ── Routes ────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Main page — display account balance and warehouse inventory."""
    try:
        account = get_account()
        products = Product.query.order_by(Product.name).all()
        return render_template("db_index.html", balance=account.balance, products=products)
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("db_index.html", balance=0.0, products=[])


@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    """Purchase form — add products to warehouse, debit account."""
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            price_str = request.form.get("price", "").strip()
            quantity_str = request.form.get("quantity", "").strip()

            # Validate inputs
            if not name:
                flash("Product name is required.", "error")
                return redirect(url_for("purchase"))

            try:
                price = float(price_str)
            except (ValueError, TypeError):
                flash("Price must be a valid number.", "error")
                return redirect(url_for("purchase"))

            try:
                quantity = int(quantity_str)
            except (ValueError, TypeError):
                flash("Quantity must be a valid whole number.", "error")
                return redirect(url_for("purchase"))

            if price < 0:
                flash("Price cannot be negative.", "error")
                return redirect(url_for("purchase"))

            if quantity <= 0:
                flash("Quantity must be positive.", "error")
                return redirect(url_for("purchase"))

            total = price * quantity
            account = get_account()

            if account.balance < total:
                flash(f"Insufficient funds. Cost: {total:.2f}, Balance: {account.balance:.2f}", "error")
                return redirect(url_for("purchase"))

            # Debit account
            account.balance -= total

            # Add or update product
            product = Product.query.filter_by(name=name).first()
            if product:
                product.quantity += quantity
                product.price = price
            else:
                product = Product(name=name, price=price, quantity=quantity)
                db.session.add(product)

            db.session.commit()

            log_transaction(
                "purchase",
                f"Purchased {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {account.balance:.2f}",
            )

            flash(f"Purchased {quantity}x '{name}' for {total:.2f}.", "success")
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}", "error")
            return redirect(url_for("purchase"))

    return render_template("db_purchase.html")


@app.route("/sale", methods=["GET", "POST"])
def sale():
    """Sale form — remove products from warehouse, credit account."""
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            price_str = request.form.get("price", "").strip()
            quantity_str = request.form.get("quantity", "").strip()

            # Validate inputs
            if not name:
                flash("Product name is required.", "error")
                return redirect(url_for("sale"))

            try:
                price = float(price_str)
            except (ValueError, TypeError):
                flash("Price must be a valid number.", "error")
                return redirect(url_for("sale"))

            try:
                quantity = int(quantity_str)
            except (ValueError, TypeError):
                flash("Quantity must be a valid whole number.", "error")
                return redirect(url_for("sale"))

            if price < 0:
                flash("Price cannot be negative.", "error")
                return redirect(url_for("sale"))

            if quantity <= 0:
                flash("Quantity must be positive.", "error")
                return redirect(url_for("sale"))

            # Check stock
            product = Product.query.filter_by(name=name).first()
            if not product:
                flash(f"'{name}' not found in warehouse.", "error")
                return redirect(url_for("sale"))

            if product.quantity < quantity:
                flash(f"Insufficient stock. Only {product.quantity} unit(s) of '{name}' available.", "error")
                return redirect(url_for("sale"))

            total = price * quantity
            account = get_account()

            # Credit account
            account.balance += total

            # Reduce stock
            product.quantity -= quantity
            if product.quantity == 0:
                db.session.delete(product)

            db.session.commit()

            log_transaction(
                "sale",
                f"Sold {quantity}x '{name}' @ {price:.2f} = {total:.2f}. Balance: {account.balance:.2f}",
            )

            flash(f"Sold {quantity}x '{name}' for {total:.2f}.", "success")
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}", "error")
            return redirect(url_for("sale"))

    return render_template("db_sale.html")


@app.route("/balance", methods=["GET", "POST"])
def balance():
    """Balance form — add or subtract from account."""
    if request.method == "POST":
        try:
            operation = request.form.get("operation", "").strip()
            amount_str = request.form.get("amount", "").strip()

            if operation not in ("add", "subtract"):
                flash("Please select 'add' or 'subtract'.", "error")
                return redirect(url_for("balance"))

            try:
                amount = float(amount_str)
            except (ValueError, TypeError):
                flash("Amount must be a valid number.", "error")
                return redirect(url_for("balance"))

            if amount < 0:
                flash("Amount cannot be negative.", "error")
                return redirect(url_for("balance"))

            account = get_account()

            if operation == "add":
                account.balance += amount
                action_desc = f"Added {amount:.2f} to account."
            else:
                account.balance -= amount
                action_desc = f"Subtracted {amount:.2f} from account."

            db.session.commit()

            log_transaction("balance", f"{action_desc} New balance: {account.balance:.2f}")

            flash(f"{action_desc} Balance: {account.balance:.2f}", "success")
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}", "error")
            return redirect(url_for("balance"))

    return render_template("db_balance.html")


@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History page — display transaction log with optional range."""
    try:
        all_transactions = Transaction.query.order_by(Transaction.id).all()
        total = len(all_transactions)

        if line_from is not None and line_to is not None:
            # Clamp indices to valid range
            actual_from = max(0, line_from)
            actual_to = min(total, line_to + 1)

            if actual_from != line_from or actual_to != line_to + 1:
                flash(
                    f"Range adjusted to [{actual_from}–{actual_to - 1}] (total: {total} entries).",
                    "warning",
                )

            if actual_from >= actual_to:
                flash("Invalid range: 'from' must be less than 'to'.", "error")
                transactions = []
            else:
                transactions = all_transactions[actual_from:actual_to]

            showing_range = True
            range_from = actual_from
            range_to = actual_to - 1
        else:
            transactions = all_transactions
            showing_range = False
            range_from = 0
            range_to = total - 1 if total > 0 else 0

        return render_template(
            "db_history.html",
            transactions=transactions,
            total=total,
            showing_range=showing_range,
            range_from=range_from,
            range_to=range_to,
        )

    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template(
            "db_history.html",
            transactions=[],
            total=0,
            showing_range=False,
            range_from=0,
            range_to=0,
        )


# ── App Startup ───────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    print("\n  Inventory Manager (SQLite) running on http://localhost:5002\n")
    app.run(debug=True, port=5002)
