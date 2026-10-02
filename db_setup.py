"""
================================================================================
HOTEL RESERVATION MANAGEMENT SYSTEM - DATABASE SETUP & SEED UTILITY
Run this script to initialize or reset the database from the terminal.
================================================================================
"""

import sys
from database import init_db, query_db

def main():
    print("Initializing Hotel Reservation Database...")
    init_db(force_reset=True)
    
    print("\n--- DATABASE SUMMARY REPORT ---")
    tables = ["Room_Types", "Rooms", "Guests", "Staff", "Reservations", "Payments"]
    for t in tables:
        count = query_db(f"SELECT COUNT(*) AS count FROM {t};", one=True)["count"]
        print(f"  Table '{t}': {count} records")

    print("\nDatabase initialization complete! File: hotel_database.db")
    print("Ready to start server: python app.py")

if __name__ == "__main__":
    main()
