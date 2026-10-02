-- ============================================================================
-- HOTEL RESERVATION MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Relational DBMS Schema with Keys, Constraints, Foreign Keys & Triggers
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. ROOM TYPES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Room_Types (
    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price_per_night REAL NOT NULL CHECK (price_per_night > 0),
    capacity INTEGER NOT NULL CHECK (capacity >= 1 AND capacity <= 10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. ROOMS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT NOT NULL UNIQUE,
    room_type_id INTEGER NOT NULL,
    floor INTEGER NOT NULL CHECK (floor >= 1 AND floor <= 50),
    status TEXT NOT NULL DEFAULT 'Available' 
        CHECK (status IN ('Available', 'Occupied', 'Reserved', 'Maintenance')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id)
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- 3. GUESTS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Guests (
    guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL CHECK (length(trim(guest_name)) >= 2),
    phone TEXT NOT NULL UNIQUE CHECK (length(phone) >= 7),
    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@__%.__%'),
    address TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 4. STAFF TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_name TEXT NOT NULL CHECK (length(trim(staff_name)) >= 2),
    role TEXT NOT NULL CHECK (role IN (
        'Hotel Manager', 
        'Front Desk Executive', 
        'Concierge', 
        'Housekeeping Supervisor', 
        'Maintenance Engineer', 
        'Accountant',
        'Executive Chef'
    )),
    phone TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@__%.__%'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. RESERVATIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    number_of_guests INTEGER NOT NULL CHECK (number_of_guests >= 1),
    reservation_status TEXT NOT NULL DEFAULT 'Confirmed' 
        CHECK (reservation_status IN ('Confirmed', 'Checked-In', 'Checked-Out', 'Cancelled')),
    total_price REAL NOT NULL CHECK (total_price >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_dates CHECK (date(check_out) > date(check_in)),
    FOREIGN KEY (guest_id) REFERENCES Guests(guest_id)
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- 6. PAYMENTS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    guest_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    payment_date TEXT NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('Cash', 'Card', 'UPI')),
    payment_status TEXT NOT NULL DEFAULT 'Paid' CHECK (payment_status IN ('Paid', 'Pending', 'Refunded')),
    transaction_ref TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES Reservations(reservation_id)
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY (guest_id) REFERENCES Guests(guest_id)
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- PERFORMANCE INDEXES (FOR EFFICIENT JOINS & LOOKUPS)
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_rooms_type ON Rooms(room_type_id);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON Rooms(status);
CREATE INDEX IF NOT EXISTS idx_reservations_room ON Reservations(room_id);
CREATE INDEX IF NOT EXISTS idx_reservations_guest ON Reservations(guest_id);
CREATE INDEX IF NOT EXISTS idx_reservations_dates ON Reservations(check_in, check_out);
CREATE INDEX IF NOT EXISTS idx_payments_reservation ON Payments(reservation_id);
CREATE INDEX IF NOT EXISTS idx_payments_guest ON Payments(guest_id);

-- ----------------------------------------------------------------------------
-- TRIGGERS FOR AUTOMATED ROOM STATUS SYNCHRONIZATION
-- ----------------------------------------------------------------------------

-- Trigger 1: When reservation is marked 'Checked-In', set Room to 'Occupied'
CREATE TRIGGER IF NOT EXISTS trg_reservation_checkin
AFTER UPDATE OF reservation_status ON Reservations
FOR EACH ROW
WHEN NEW.reservation_status = 'Checked-In'
BEGIN
    UPDATE Rooms SET status = 'Occupied' WHERE room_id = NEW.room_id;
END;

-- Trigger 2: When reservation is marked 'Checked-Out' or 'Cancelled', restore Room to 'Available'
CREATE TRIGGER IF NOT EXISTS trg_reservation_checkout
AFTER UPDATE OF reservation_status ON Reservations
FOR EACH ROW
WHEN NEW.reservation_status IN ('Checked-Out', 'Cancelled')
BEGIN
    UPDATE Rooms SET status = 'Available' WHERE room_id = NEW.room_id;
END;
