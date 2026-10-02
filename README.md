# 🏨 Grand Horizon - Hotel Reservation Management System

A modern, responsive, full-stack **Hotel Reservation Management System (HMS)** engineered for an academic **Database Management Systems (DBMS)** project. 

This application demonstrates relational modeling, primary and foreign key constraints, check constraints, database triggers, multi-table SQL `JOIN`s, and transactional integrity (including double-booking prevention and automated room status synchronization).

---

## 🌟 Key Highlights & Academic DBMS Features

1. **Relational Data Model & Integrity**:
   - **6 Relational Entities**: `Room_Types`, `Rooms`, `Guests`, `Staff`, `Reservations`, `Payments`.
   - **Primary Keys (`PK`)**: Auto-incrementing integer identifier on every table.
   - **Foreign Keys (`FK`)**:
     - `Rooms(room_type_id) REFERENCES Room_Types(room_type_id)` (`ON DELETE RESTRICT`)
     - `Reservations(guest_id) REFERENCES Guests(guest_id)` (`ON DELETE RESTRICT`)
     - `Reservations(room_id) REFERENCES Rooms(room_id)` (`ON DELETE RESTRICT`)
     - `Payments(reservation_id) REFERENCES Reservations(reservation_id)` (`ON DELETE CASCADE`)
     - `Payments(guest_id) REFERENCES Guests(guest_id)` (`ON DELETE RESTRICT`)
   - **CHECK Constraints**:
     - `price_per_night > 0`
     - `capacity >= 1 AND capacity <= 10`
     - `date(check_out) > date(check_in)` (Strict reservation timeline)
     - `number_of_guests >= 1`
     - `amount >= 0`
     - `status IN ('Available', 'Occupied', 'Reserved', 'Maintenance')`
     - `reservation_status IN ('Confirmed', 'Checked-In', 'Checked-Out', 'Cancelled')`
     - `payment_method IN ('Cash', 'Card', 'UPI')`
     - `payment_status IN ('Paid', 'Pending', 'Refunded')`
   - **UNIQUE Constraints**: Room numbers, guest emails, guest phones, room type names, staff emails, and transaction references.
   - **Database Triggers**:
     - `trg_reservation_checkin`: When a reservation is updated to `Checked-In`, the assigned room automatically switches to `Occupied`.
     - `trg_reservation_checkout`: When a reservation is updated to `Checked-Out` or `Cancelled`, the assigned room automatically reverts to `Available`.

2. **Double-Booking Prevention Logic**:
   - Dynamic date-range overlap detection prevents selecting any room that is currently reserved or checked-in during the requested `[check_in, check_out]` interval:
     $$\text{Conflict: } (\text{existing.check\_in} < \text{new.check\_out}) \land (\text{existing.check\_out} > \text{new.check\_in})$$

3. **Academic DBMS Explorer Tab**:
   - Built-in interactive **DBMS Explorer** displaying the Entity-Relationship Diagram (ERD), live table schemas from SQLite metadata, and the exact underlying SQL statements used for queries, joins, and aggregates.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask 3.1 REST API, SQLite 3 (with foreign key enforcement enabled via `PRAGMA foreign_keys = ON`).
- **Database Engine**: SQLite (default zero-configuration file `hotel_database.db`; easily configurable for MySQL / PostgreSQL in `database.py`).
- **Frontend**: HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid, Responsive Media Queries), Vanilla ES6+ Modular Components, Chart.js for reports, and FontAwesome 6 icons.

---

## 📁 Project Structure

```
hotel-reservation-system/
│
├── app.py                      # Flask REST API server and routing
├── database.py                 # SQLite connection manager & query helpers
├── schema.sql                  # DDL: Tables, constraints, foreign keys, triggers, indexes
├── seed.sql                    # DML: Realistic sample dataset (5 room types, 16 rooms, 10 guests, 8 staff, 10 reservations, 10 payments)
├── db_setup.py                 # Terminal utility to initialize or reset database
├── test_api.py                 # Automated integrity test suite (10 test cases)
├── test_frontend.py            # Automated asset & template loading verification
├── run.bat                     # 1-click Windows application launcher
├── README.md                   # Full documentation & project guide
│
├── templates/
│   └── index.html              # Main Single-Page Application (SPA) HTML5 shell
│
└── static/
    ├── css/
    │   └── styles.css          # Luxury hotel styling, dark/light theme, responsive layout
    └── js/
        ├── api.js              # REST API client
        ├── app.js              # Master application controller, router, modals, toasts
        └── components/
            ├── dashboard.js    # Executive KPIs, floor matrix, recent bookings
            ├── roomTypes.js    # Room types management & capacity constraints
            ├── rooms.js        # Rooms inventory, status filters, floor plans
            ├── guests.js       # Guest directory & historical bookings
            ├── reservations.js # Interactive Make Reservation flow & check-in/out
            ├── payments.js     # Billing records, payment methods, receipts
            ├── staff.js        # Staff directory & role privileges
            ├── reports.js      # Group By summaries & Chart.js visualizations
            └── dbmsExplorer.js # ERD diagram, live schema inspector, SQL viewer
```

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.8+ (Python 3.14+ supported)
- Flask (`pip install Flask` if not already installed)

### Step 1: Open Terminal in the Project Directory
```powershell
cd C:\Users\keerthana\.gemini\antigravity\scratch\hotel-reservation-system
```

### Step 2: Initialize Database (Optional, done automatically)
```powershell
python db_setup.py
```

### Step 3: Run the Automated Verification Tests
```powershell
python test_api.py
python test_frontend.py
```
*All tests should pass with code 0.*

### Step 4: Start the Web Application
```powershell
python app.py
```
Or on Windows, simply double-click `run.bat`.

### Step 5: Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 🗄️ How the Database Connection is Configured

Database connections are managed centrally in `database.py`.

### Default SQLite Configuration:
```python
def get_db_connection():
    conn = sqlite3.connect("hotel_database.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;") # Enforces referential integrity
    return conn
```

### Switching to MySQL (e.g. for MySQL Workbench):
In `database.py`, modify `get_db_connection()`:
```python
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="hotel_db"
    )
```

### Switching to PostgreSQL:
```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="hotel_db",
        user="postgres",
        password="your_password",
        cursor_factory=RealDictCursor
    )
```

---

## 🔄 How to Add or Modify Sample Data

1. **Via the User Interface**:
   - Click **Make Reservation** to add bookings.
   - Click **Register New Guest** under Guests.
   - Click **Add Room** under Rooms.
   - Click **Record Payment** under Payments.
   - Click **Reset Sample Data** in the top navigation bar anytime to return to a clean baseline.

2. **Via the SQL Seed File (`seed.sql`)**:
   - Open `seed.sql` in any text editor.
   - Edit or add `INSERT INTO` statements.
   - Run `python db_setup.py` to reload the database.

---

## 💻 Pages & Features Walkthrough

1. **Dashboard**:
   - Metric cards: Total Rooms, Available Rooms, Occupied Rooms, Total Guests, Total Reservations, Gross Revenue.
   - Interactive 16-room Floor Matrix color-coded by real-time status.
   - Recent reservations log with status badges.
   - Room occupancy progress bars.

2. **Room Types**:
   - Cards and table view displaying category ID, name, description, price per night, and capacity.
   - Add/Edit/Delete modals with DBMS check constraint validation (`price > 0`, `capacity 1..10`).
   - Prevents deleting room types that have rooms assigned (`FOREIGN KEY RESTRICT`).

3. **Rooms**:
   - Lists all rooms with Floor, Room Number, Type, Rate, and Status.
   - Filters by Status (`Available`, `Occupied`, `Reserved`, `Maintenance`), Floor (`1-4`), and Category.
   - Toggle between Table and Grid view.
   - Add/Edit/Delete room dialogs.

4. **Guests**:
   - Full guest directory with name, unique phone, unique email, and postal address.
   - Interactive **History** button showing each guest's individual booking records and receipts.
   - Prevents deleting guests with active reservations.

5. **Reservations & Make Reservation Flow**:
   - **Step 1**: Select guest (or click "+ New Guest" for quick registration).
   - **Step 2**: Select check-in and check-out dates.
   - **Step 3**: Specify number of guests.
   - **Step 4**: Dynamic Available Rooms dropdown queries the database to show only rooms without schedule conflicts.
   - **Step 5**: Real-time live price preview ($/night $\times$ nights).
   - **Step 6**: Connected payment option (`Card`, `UPI`, `Cash`).
   - Status actions: **Check In** (switches room to `Occupied`), **Check Out** (switches room to `Available`), and **Cancel**.

6. **Payments**:
   - Financial summaries: Settled Revenue (Paid), Pending Balances, Refunded Amounts.
   - Filter by payment method (`Card`, `UPI`, `Cash`) and status (`Paid`, `Pending`, `Refunded`).
   - Generate official printable Hotel Folios / Receipts.

7. **Staff**:
   - Employee records with designated roles: Hotel Manager, Front Desk Executive, Concierge, Housekeeping Supervisor, Maintenance Engineer, Accountant, Executive Chef.

8. **Reports & Analytics**:
   - Interactive Chart.js graphs:
     - Most frequently reserved room types (Bar chart)
     - Reservation status distribution (Donut chart)
     - Room availability breakdown (Donut chart)
     - Payment methods & volume (Bar chart)
   - Detailed revenue table with percentage contribution bars.
   - Printable report view.

9. **DBMS Relational Explorer**:
   - Complete ER diagram showing entity relationships and cardinalities.
   - Live inspection of tables, data types, primary keys, and foreign keys.
   - Query showcase highlighting the exact SQL used for availability checks, joins, aggregates, and triggers.
