"""
================================================================================
HOTEL RESERVATION MANAGEMENT SYSTEM - DATABASE LAYER
Relational DBMS Connection Manager, Schema Initializer, and Query Controller
================================================================================
"""

import os
import sqlite3
from contextlib import contextmanager

# Path to database file
DB_NAME = "hotel_database.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed.sql")


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    CRITICAL DBMS CONFIGURATION:
    - row_factory is set to sqlite3.Row for dictionary-like column access.
    - PRAGMA foreign_keys = ON is explicitly executed to enforce relational integrity.
    
    ----------------------------------------------------------------------------
    [DBMS CONFIGURATION GUIDE: CONNECTING TO MYSQL OR POSTGRESQL]
    To switch from SQLite to MySQL or PostgreSQL for your university DBMS lab:
    
    For MySQL:
      import mysql.connector
      return mysql.connector.connect(
          host="localhost",
          user="root",
          password="your_password",
          database="hotel_db"
      )
      
    For PostgreSQL:
      import psycopg2
      from psycopg2.extras import RealDictCursor
      return psycopg2.connect(
          host="localhost",
          database="hotel_db",
          user="postgres",
          password="your_password",
          cursor_factory=RealDictCursor
      )
    ----------------------------------------------------------------------------
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce Foreign Key constraints in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_cursor(commit=False):
    """Context manager for safe database transactions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def query_db(query, args=(), one=False):
    """Executes a SELECT query and returns records as Python dicts."""
    with db_cursor() as cursor:
        cursor.execute(query, args)
        rv = cursor.fetchall()
        result = [dict(row) for row in rv]
        return (result[0] if result else None) if one else result


def execute_db(query, args=()):
    """Executes an INSERT, UPDATE, or DELETE query within an auto-commit transaction."""
    with db_cursor(commit=True) as cursor:
        cursor.execute(query, args)
        return {
            "last_row_id": cursor.lastrowid,
            "rows_affected": cursor.rowcount
        }


def init_db(force_reset=False):
    """
    Initializes the database using schema.sql and seed.sql.
    If force_reset is True, any existing database is removed and recreated.
    """
    if force_reset and os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[DBMS] Removed existing database: {DB_PATH}")
        except Exception as e:
            print(f"[DBMS Warning] Could not remove existing db file: {e}")

    conn = get_db_connection()
    with conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        print("[DBMS] Schema applied successfully with constraints, keys & triggers.")

        # Check if seed data is needed
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM Room_Types")
        row = cursor.fetchone()
        if row["count"] == 0 or force_reset:
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            print("[DBMS] Seed dataset injected successfully.")
        else:
            print("[DBMS] Database already contains records. Skipping seed.")
    conn.close()


# ==============================================================================
# SPECIALIZED DBMS BUSINESS LOGIC & VALIDATION HELPERS
# ==============================================================================

def check_room_availability(room_id, check_in, check_out, exclude_reservation_id=None):
    """
    Validates if a room is available for the specified date range [check_in, check_out].
    Prevents double-booking!
    
    A room is unavailable if:
    1. The room itself is marked 'Maintenance' in Rooms table.
    2. An existing reservation for that room with status in ('Confirmed', 'Checked-In')
       overlaps with the requested [check_in, check_out] period.
       Overlap logic: (existing.check_in < requested.check_out AND existing.check_out > requested.check_in)
    """
    # Check maintenance status
    room = query_db("SELECT status FROM Rooms WHERE room_id = ?", (room_id,), one=True)
    if not room:
        return False, "Room does not exist."
    if room["status"] == "Maintenance":
        return False, "This room is currently under maintenance."

    # Check date overlap with active reservations
    query = """
        SELECT reservation_id, check_in, check_out, reservation_status 
        FROM Reservations
        WHERE room_id = ? 
          AND reservation_status IN ('Confirmed', 'Checked-In')
          AND (date(check_in) < date(?) AND date(check_out) > date(?))
    """
    params = [room_id, check_out, check_in]

    if exclude_reservation_id:
        query += " AND reservation_id != ?"
        params.append(exclude_reservation_id)

    conflicting = query_db(query, tuple(params))
    if conflicting:
        conflict = conflicting[0]
        return False, f"Room is already booked from {conflict['check_in']} to {conflict['check_out']} (Reservation #{conflict['reservation_id']})."

    return True, "Room is available."


def get_available_rooms_for_dates(check_in, check_out, room_type_id=None, min_capacity=1):
    """
    Returns all rooms that are available between check_in and check_out
    and meet the capacity requirement. Uses a SQL LEFT JOIN / NOT EXISTS subquery.
    """
    query = """
        SELECT 
            r.room_id,
            r.room_number,
            r.floor,
            r.status AS current_status,
            rt.room_type_id,
            rt.room_type,
            rt.price_per_night,
            rt.capacity,
            rt.description
        FROM Rooms r
        JOIN Room_Types rt ON r.room_type_id = rt.room_type_id
        WHERE r.status != 'Maintenance'
          AND rt.capacity >= ?
          AND NOT EXISTS (
              SELECT 1 FROM Reservations res
              WHERE res.room_id = r.room_id
                AND res.reservation_status IN ('Confirmed', 'Checked-In')
                AND (date(res.check_in) < date(?) AND date(res.check_out) > date(?))
          )
    """
    params = [min_capacity, check_out, check_in]
    if room_type_id:
        query += " AND rt.room_type_id = ?"
        params.append(room_type_id)

    query += " ORDER BY r.floor ASC, r.room_number ASC"
    return query_db(query, tuple(params))


def sync_all_room_statuses():
    """
    Synchronizes room statuses based on today's active reservations.
    If a room has a Checked-In reservation today -> Occupied.
    If a room has a Confirmed reservation starting today -> Reserved.
    Otherwise (if not Maintenance) -> Available.
    """
    today_query = """
        UPDATE Rooms 
        SET status = CASE 
            WHEN status = 'Maintenance' THEN 'Maintenance'
            WHEN room_id IN (
                SELECT room_id FROM Reservations 
                WHERE reservation_status = 'Checked-In'
            ) THEN 'Occupied'
            WHEN room_id IN (
                SELECT room_id FROM Reservations 
                WHERE reservation_status = 'Confirmed'
                  AND date(check_in) <= date('now')
                  AND date(check_out) > date('now')
            ) THEN 'Reserved'
            ELSE 'Available'
        END;
    """
    with db_cursor(commit=True) as cursor:
        cursor.execute(today_query)


if __name__ == "__main__":
    init_db(force_reset=True)
    print("Database initial verification complete.")
