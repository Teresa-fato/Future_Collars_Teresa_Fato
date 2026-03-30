"""
Gym Course Booking System — Flask + SQLAlchemy + Spectre.css
Manages courses, clients, bookings, and booking history.

Usage:
    pip install flask flask-sqlalchemy
    python app.py

Opens on http://localhost:5003
"""

import os
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# ── App Configuration ─────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "gym_booking_secret_key_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'gym_bookings.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ── Database Models ───────────────────────────────────────────────────


class Client(db.Model):
    """Represents a gym client."""
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    bookings = db.relationship("Booking", backref="client", lazy=True)

    def full_name(self):
        return f"{self.name} {self.surname}"


class Course(db.Model):
    """Represents a gym course."""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False, default=20)
    bookings = db.relationship("Booking", backref="course", lazy=True)


class Booking(db.Model):
    """Represents a course booking."""
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    time = db.Column(db.String(5), nullable=False)    # HH:MM
    status = db.Column(db.String(20), nullable=False, default="booked")  # booked / cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Seed Data ─────────────────────────────────────────────────────────


def seed_courses():
    """Add default courses if the table is empty."""
    if Course.query.count() == 0:
        default_courses = [
            Course(name="Yoga", price=15.00, available_spots=20),
            Course(name="Spinning", price=12.00, available_spots=15),
            Course(name="CrossFit", price=20.00, available_spots=12),
            Course(name="Pilates", price=18.00, available_spots=18),
            Course(name="Zumba", price=10.00, available_spots=25),
        ]
        db.session.add_all(default_courses)
        db.session.commit()


# ── Validation Helpers ────────────────────────────────────────────────


def is_valid_email(email):
    """Check if email format is valid."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


# ── Routes ────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Main page — display available courses and navigation."""
    try:
        courses = Course.query.all()
    except Exception as e:
        flash(f"Database error: {e}", "error")
        courses = []
    return render_template("index.html", courses=courses)


@app.route("/booking", methods=["GET", "POST"])
def booking():
    """Booking form — book a course for a client."""
    if request.method == "POST":
        try:
            client_id = request.form.get("client_id", "").strip()
            course_id = request.form.get("course_id", "").strip()
            date = request.form.get("date", "").strip()
            time = request.form.get("time", "").strip()

            # Validate required fields
            if not all([client_id, course_id, date, time]):
                flash("All fields are required.", "error")
                return redirect(url_for("booking"))

            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format. Use YYYY-MM-DD.", "error")
                return redirect(url_for("booking"))

            # Validate time format
            try:
                datetime.strptime(time, "%H:%M")
            except ValueError:
                flash("Invalid time format. Use HH:MM.", "error")
                return redirect(url_for("booking"))

            # Check client exists
            client = Client.query.get(int(client_id))
            if not client:
                flash("Client not found.", "error")
                return redirect(url_for("booking"))

            # Check course exists and has spots
            course = Course.query.get(int(course_id))
            if not course:
                flash("Course not found.", "error")
                return redirect(url_for("booking"))

            if course.available_spots <= 0:
                flash(f"No available spots for '{course.name}'.", "error")
                return redirect(url_for("booking"))

            # Create booking
            new_booking = Booking(
                client_id=client.id,
                course_id=course.id,
                date=date,
                time=time,
                status="booked",
            )
            course.available_spots -= 1
            db.session.add(new_booking)
            db.session.commit()

            flash(f"Booking confirmed: {client.full_name()} → {course.name} on {date} at {time}", "success")
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating booking: {e}", "error")
            return redirect(url_for("booking"))

    # GET — display form
    clients = Client.query.order_by(Client.surname).all()
    courses = Course.query.filter(Course.available_spots > 0).all()
    return render_template("booking.html", clients=clients, courses=courses)


@app.route("/client", methods=["GET", "POST"])
def client():
    """Client form — register a new client."""
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            surname = request.form.get("surname", "").strip()
            email = request.form.get("email", "").strip()

            # Validate required fields
            if not name:
                flash("First name is required.", "error")
                return redirect(url_for("client"))

            if not surname:
                flash("Last name is required.", "error")
                return redirect(url_for("client"))

            if not email:
                flash("Email is required.", "error")
                return redirect(url_for("client"))

            # Validate email format
            if not is_valid_email(email):
                flash("Invalid email format.", "error")
                return redirect(url_for("client"))

            # Check if email already exists
            existing = Client.query.filter_by(email=email).first()
            if existing:
                flash(f"A client with email '{email}' already exists.", "error")
                return redirect(url_for("client"))

            # Create client
            new_client = Client(name=name, surname=surname, email=email)
            db.session.add(new_client)
            db.session.commit()

            flash(f"Client registered: {name} {surname} ({email})", "success")
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error registering client: {e}", "error")
            return redirect(url_for("client"))

    # GET — display form
    return render_template("client.html")


@app.route("/manage", methods=["GET", "POST"])
def manage():
    """Manage bookings — update booking status."""
    if request.method == "POST":
        try:
            booking_id = request.form.get("booking_id", "").strip()
            new_status = request.form.get("status", "").strip()

            if not booking_id or not new_status:
                flash("Please select a booking and a status.", "error")
                return redirect(url_for("manage"))

            if new_status not in ("booked", "cancelled"):
                flash("Invalid status. Must be 'booked' or 'cancelled'.", "error")
                return redirect(url_for("manage"))

            booking_record = Booking.query.get(int(booking_id))
            if not booking_record:
                flash("Booking not found.", "error")
                return redirect(url_for("manage"))

            old_status = booking_record.status

            # Update spots based on status change
            if old_status == "booked" and new_status == "cancelled":
                booking_record.course.available_spots += 1
            elif old_status == "cancelled" and new_status == "booked":
                if booking_record.course.available_spots <= 0:
                    flash(f"No available spots for '{booking_record.course.name}'.", "error")
                    return redirect(url_for("manage"))
                booking_record.course.available_spots -= 1

            booking_record.status = new_status
            db.session.commit()

            flash(f"Booking #{booking_id} updated: {old_status} → {new_status}", "success")
            return redirect(url_for("manage"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating booking: {e}", "error")
            return redirect(url_for("manage"))

    # GET — display form with all bookings
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("manage.html", bookings=bookings)


@app.route("/history")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History page — display booking history with optional range."""
    try:
        all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        total = len(all_bookings)

        if line_from is not None and line_to is not None:
            # Clamp to valid range
            if line_from < 0:
                line_from = 0
            if line_to > total:
                line_to = total
            if line_from >= line_to:
                flash(f"Invalid range: {line_from}–{line_to}.", "error")
                bookings = all_bookings
                line_from = None
                line_to = None
            else:
                bookings = all_bookings[line_from:line_to]
        else:
            bookings = all_bookings

    except Exception as e:
        flash(f"Database error: {e}", "error")
        bookings = []
        total = 0

    return render_template(
        "history.html",
        bookings=bookings,
        line_from=line_from,
        line_to=line_to,
        total=total,
    )


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_courses()
    app.run(debug=True, port=5003)
