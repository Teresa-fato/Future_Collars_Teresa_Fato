# 🏋️ Gym Course Booking System

A web application for managing gym course bookings built with **Flask**, **Flask-SQLAlchemy**, and **Spectre.css**.

---

## 📁 Project Structure

```
gym_booking_system/
├── app.py                  ← Main Flask application (routes + models)
├── requirements.txt        ← Python dependencies
├── .gitignore              ← Excludes database + cache files
├── README.md               ← This file
└── templates/
    ├── base.html           ← Base layout (navbar, flash messages, Spectre.css)
    ├── index.html          ← Dashboard: course list + navigation buttons
    ├── booking.html        ← Booking form (client + course + date/time)
    ├── client.html         ← Client registration form
    ├── manage.html         ← Booking management (update status)
    └── history.html        ← Booking history with range filter
```

---

## 🚀 How to Run

### 1. Install Python dependencies

```bash
cd gym_booking_system
pip install -r requirements.txt
```

### 2. Run the application

```bash
python app.py
```

### 3. Open in your browser

```
http://localhost:5003
```

The database (`gym_bookings.db`) is created automatically on first run, along with 5 default courses.

---

## 📄 Pages & Features

### 🏠 Home Page (`/`)
- Displays all available gym courses in a table
- Shows **course name**, **price**, **available spots**, and **status** (Available / Few spots left / Full)
- Navigation buttons to all other pages

### 📅 Book a Course (`/booking`)
- **Dropdown** to select a registered client
- **Dropdown** to select a course (only courses with available spots)
- **Date picker** and **time picker** for scheduling
- On successful booking:
  - Available spots decrease by 1
  - Success message displayed
  - Redirects to home page
- Validation: all fields required, date/time format checked

### 👤 Register Client (`/client`)
- Fields: **First name**, **Last name**, **Email**
- Email validation (format check + uniqueness)
- On success: redirects to home page with confirmation

### ⚙️ Manage Bookings (`/manage`)
- **Dropdown** to select an existing booking
- **Radio buttons** to set status: `booked` or `cancelled`
- When cancelling: available spots increase by 1
- When re-booking: checks if spots are available
- Displays a table of all current bookings below the form

### 📋 Booking History (`/history`)
- Displays all bookings with: client name, course, date, time, status, created timestamp
- **Optional range filter**: enter "From" and "To" indices to filter results
- URL patterns:
  - `/history/` — show all bookings
  - `/history/0/5/` — show bookings 0 through 4
- Out-of-range values are automatically clamped

---

## 🗄️ Database Schema

The application uses **SQLite** via **Flask-SQLAlchemy**. The database file (`gym_bookings.db`) is created automatically and excluded from version control.

### Tables

| Table      | Columns                                              | Description                  |
|------------|------------------------------------------------------|------------------------------|
| `clients`  | `id`, `name`, `surname`, `email` (unique)            | Registered gym clients       |
| `courses`  | `id`, `name` (unique), `price`, `available_spots`    | Available gym courses        |
| `bookings` | `id`, `client_id` (FK), `course_id` (FK), `date`, `time`, `status`, `created_at` | Booking records |

### Relationships
- A **Client** can have many **Bookings** (one-to-many)
- A **Course** can have many **Bookings** (one-to-many)
- Each **Booking** belongs to exactly one Client and one Course

---

## 🎨 Frontend

- **Spectre.css** (loaded via CDN) for responsive, clean styling
- Flash messages appear as toast notifications (green for success, red for errors)
- Color-coded status labels: 🟢 booked / 🔴 cancelled
- Course availability badges: 🟢 Available / 🟡 Few spots left / 🔴 Full

---

## ✅ Validation & Error Handling

| Scenario                         | Behavior                                  |
|----------------------------------|-------------------------------------------|
| Missing required fields          | Flash error, redirect back to form        |
| Invalid email format             | Flash error, redirect back                |
| Duplicate email registration     | Flash error, redirect back                |
| No available spots for course    | Flash error, redirect back                |
| Invalid date/time format         | Flash error, redirect back                |
| Database error                   | Rollback transaction, flash error message |
| Invalid history range            | Shows all records, flash warning          |

---

## 🌱 Default Courses

On first run, 5 courses are automatically seeded:

| Course    | Price  | Spots |
|-----------|--------|-------|
| Yoga      | €15.00 | 20    |
| Spinning  | €12.00 | 15    |
| CrossFit  | €20.00 | 12    |
| Pilates   | €18.00 | 18    |
| Zumba     | €10.00 | 25    |

---

## 🔧 Technologies Used

- **Python 3** — programming language
- **Flask** — lightweight web framework
- **Flask-SQLAlchemy** — ORM for SQLite database
- **SQLite** — embedded relational database
- **Spectre.css** — lightweight CSS framework (via CDN)
- **Jinja2** — HTML templating engine (built into Flask)
