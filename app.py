"""
================================================================================
HOTEL RESERVATION MANAGEMENT SYSTEM - FLASK REST API & WEB SERVER
Academic DBMS Demonstration Application
================================================================================
"""

import os
import re
import datetime
from flask import Flask, jsonify, request, render_template, send_from_directory
import database as db

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configure CORS headers for all responses so any frontend client can connect
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


# ------------------------------------------------------------------------------
# FRONTEND ROUTE
# ------------------------------------------------------------------------------
@app.route("/")
def index():
    """Serves the main single-page application interface."""
    return render_template("index.html")


# ==============================================================================
# 1. DASHBOARD & ANALYTICS APIs
# ==============================================================================

@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Returns aggregated high-level KPIs for the hotel dashboard."""
    # Ensure room statuses match current active reservations
    db.sync_all_room_statuses()

    # Total rooms & by status
    room_stats = db.query_db("""
        SELECT 
            COUNT(*) AS total_rooms,
            SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
            SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
            SUM(CASE WHEN status = 'Reserved' THEN 1 ELSE 0 END) AS reserved_rooms,
            SUM(CASE WHEN status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms
        FROM Rooms;
    """, one=True)

    # Total guests
    guest_stats = db.query_db("SELECT COUNT(*) AS total_guests FROM Guests;", one=True)

    # Total reservations
    res_stats = db.query_db("""
        SELECT 
            COUNT(*) AS total_reservations,
            SUM(CASE WHEN reservation_status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed_count,
            SUM(CASE WHEN reservation_status = 'Checked-In' THEN 1 ELSE 0 END) AS checked_in_count,
            SUM(CASE WHEN reservation_status = 'Checked-Out' THEN 1 ELSE 0 END) AS checked_out_count,
            SUM(CASE WHEN reservation_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count
        FROM Reservations;
    """, one=True)

    # Total revenue from Paid payments
    rev_stats = db.query_db("""
        SELECT 
            COALESCE(SUM(CASE WHEN payment_status = 'Paid' THEN amount ELSE 0 END), 0) AS total_revenue,
            COALESCE(SUM(CASE WHEN payment_status = 'Pending' THEN amount ELSE 0 END), 0) AS pending_revenue,
            COALESCE(SUM(CASE WHEN payment_status = 'Refunded' THEN amount ELSE 0 END), 0) AS refunded_revenue
        FROM Payments;
    """, one=True)

    # Recent reservations (JOIN with Guests and Rooms)
    recent_reservations = db.query_db("""
        SELECT 
            r.reservation_id,
            r.check_in,
            r.check_out,
            r.number_of_guests,
            r.reservation_status,
            r.total_price,
            g.guest_name,
            rm.room_number,
            rt.room_type
        FROM Reservations r
        JOIN Guests g ON r.guest_id = g.guest_id
        JOIN Rooms rm ON r.room_id = rm.room_id
        JOIN Room_Types rt ON rm.room_type_id = rt.room_type_id
        ORDER BY r.reservation_id DESC
        LIMIT 6;
    """)

    # Room distribution overview
    room_distribution = db.query_db("""
        SELECT 
            rm.floor,
            rm.room_id,
            rm.room_number,
            rm.status,
            rt.room_type,
            rt.price_per_night
        FROM Rooms rm
        JOIN Room_Types rt ON rm.room_type_id = rt.room_type_id
        ORDER BY rm.floor ASC, rm.room_number ASC;
    """)

    return jsonify({
        "success": True,
        "rooms": room_stats,
        "guests": guest_stats["total_guests"],
        "reservations": res_stats,
        "revenue": rev_stats,
        "recent_reservations": recent_reservations,
        "room_distribution": room_distribution
    })


@app.route("/api/reports/analytics", methods=["GET"])
def get_reports_analytics():
    """Returns in-depth DBMS aggregate reports and statistics."""
    # 1. Most frequently reserved room types
    room_type_popularity = db.query_db("""
        SELECT 
            rt.room_type,
            COUNT(r.reservation_id) AS total_bookings,
            COALESCE(SUM(r.total_price), 0) AS generated_revenue,
            ROUND(AVG(r.total_price), 2) AS avg_booking_value
        FROM Room_Types rt
        LEFT JOIN Rooms rm ON rt.room_type_id = rm.room_type_id
        LEFT JOIN Reservations r ON rm.room_id = r.room_id
        GROUP BY rt.room_type_id, rt.room_type
        ORDER BY total_bookings DESC;
    """)

    # 2. Reservation status breakdown
    reservation_status_summary = db.query_db("""
        SELECT 
            reservation_status,
            COUNT(*) AS count,
            COALESCE(SUM(total_price), 0) AS total_value
        FROM Reservations
        GROUP BY reservation_status;
    """)

    # 3. Payment method & status summary
    payment_method_summary = db.query_db("""
        SELECT 
            payment_method,
            payment_status,
            COUNT(*) AS transaction_count,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM Payments
        GROUP BY payment_method, payment_status
        ORDER BY payment_method;
    """)

    # 4. Room status count
    room_status_summary = db.query_db("""
        SELECT status, COUNT(*) AS count
        FROM Rooms
        GROUP BY status;
    """)

    # 5. High-level aggregates
    total_revenue = db.query_db("SELECT COALESCE(SUM(amount), 0) AS total FROM Payments WHERE payment_status = 'Paid';", one=True)["total"]
    total_res = db.query_db("SELECT COUNT(*) AS total FROM Reservations;", one=True)["total"]
    total_rooms = db.query_db("SELECT COUNT(*) AS total FROM Rooms;", one=True)["total"]
    occupied_rooms = db.query_db("SELECT COUNT(*) AS total FROM Rooms WHERE status = 'Occupied';", one=True)["total"]
    available_rooms = db.query_db("SELECT COUNT(*) AS total FROM Rooms WHERE status = 'Available';", one=True)["total"]

    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0

    return jsonify({
        "success": True,
        "aggregates": {
            "total_revenue": total_revenue,
            "total_reservations": total_res,
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "available_rooms": available_rooms,
            "occupancy_rate": occupancy_rate
        },
        "room_type_popularity": room_type_popularity,
        "reservation_status_summary": reservation_status_summary,
        "payment_method_summary": payment_method_summary,
        "room_status_summary": room_status_summary
    })


# ==============================================================================
# 2. ROOM TYPES CRUD & FILTERING
# ==============================================================================

@app.route("/api/room-types", methods=["GET"])
def get_room_types():
    """Fetches all room types along with the number of rooms belonging to each type."""
    search = request.args.get("search", "").strip()
    query = """
        SELECT 
            rt.room_type_id,
            rt.room_type,
            rt.description,
            rt.price_per_night,
            rt.capacity,
            COUNT(rm.room_id) AS total_rooms_count
        FROM Room_Types rt
        LEFT JOIN Rooms rm ON rt.room_type_id = rm.room_type_id
    """
    params = []
    if search:
        query += " WHERE rt.room_type LIKE ? OR rt.description LIKE ?"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " GROUP BY rt.room_type_id, rt.room_type, rt.description, rt.price_per_night, rt.capacity ORDER BY rt.room_type_id ASC;"
    room_types = db.query_db(query, tuple(params))
    return jsonify({"success": True, "data": room_types})


@app.route("/api/room-types/<int:room_type_id>", methods=["GET"])
def get_single_room_type(room_type_id):
    """Fetches a single room type."""
    room_type = db.query_db("SELECT * FROM Room_Types WHERE room_type_id = ?", (room_type_id,), one=True)
    if not room_type:
        return jsonify({"success": False, "message": "Room type not found"}), 404
    return jsonify({"success": True, "data": room_type})


@app.route("/api/room-types", methods=["POST"])
def create_room_type():
    """Creates a new room type with validation."""
    data = request.get_json() or {}
    room_type = data.get("room_type", "").strip()
    description = data.get("description", "").strip()
    price_per_night = data.get("price_per_night")
    capacity = data.get("capacity")

    if not room_type:
        return jsonify({"success": False, "message": "Room type name is required."}), 400
    if not description:
        return jsonify({"success": False, "message": "Description is required."}), 400
    try:
        price_per_night = float(price_per_night)
        if price_per_night <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Price per night must be a positive number."}), 400
    try:
        capacity = int(capacity)
        if capacity < 1 or capacity > 10:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Capacity must be an integer between 1 and 10."}), 400

    try:
        res = db.execute_db("""
            INSERT INTO Room_Types (room_type, description, price_per_night, capacity)
            VALUES (?, ?, ?, ?);
        """, (room_type, description, price_per_night, capacity))
        return jsonify({
            "success": True,
            "message": f"Room type '{room_type}' created successfully.",
            "room_type_id": res["last_row_id"]
        }), 201
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": "A room type with this name already exists."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/room-types/<int:room_type_id>", methods=["PUT"])
def update_room_type(room_type_id):
    """Updates an existing room type."""
    data = request.get_json() or {}
    room_type = data.get("room_type", "").strip()
    description = data.get("description", "").strip()
    price_per_night = data.get("price_per_night")
    capacity = data.get("capacity")

    if not room_type or not description:
        return jsonify({"success": False, "message": "Name and description are required."}), 400
    try:
        price_per_night = float(price_per_night)
        if price_per_night <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Price per night must be a positive number."}), 400
    try:
        capacity = int(capacity)
        if capacity < 1 or capacity > 10:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Capacity must be between 1 and 10."}), 400

    try:
        db.execute_db("""
            UPDATE Room_Types 
            SET room_type = ?, description = ?, price_per_night = ?, capacity = ?
            WHERE room_type_id = ?;
        """, (room_type, description, price_per_night, capacity, room_type_id))
        return jsonify({"success": True, "message": "Room type updated successfully."})
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": "A room type with this name already exists."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/room-types/<int:room_type_id>", methods=["DELETE"])
def delete_room_type(room_type_id):
    """Deletes a room type, checking foreign key references."""
    # Check if rooms are currently assigned to this room type
    rooms = db.query_db("SELECT COUNT(*) AS count FROM Rooms WHERE room_type_id = ?", (room_type_id,), one=True)
    if rooms and rooms["count"] > 0:
        return jsonify({
            "success": False, 
            "message": f"Cannot delete: {rooms['count']} room(s) reference this room type. Reassign or delete those rooms first (DBMS Foreign Key RESTRICT constraint)."
        }), 409

    try:
        db.execute_db("DELETE FROM Room_Types WHERE room_type_id = ?", (room_type_id,))
        return jsonify({"success": True, "message": "Room type deleted successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# ==============================================================================
# 3. ROOMS CRUD & AVAILABILITY
# ==============================================================================

@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    """Fetches rooms with JOIN on Room_Types, supports filtering by status, floor, room_type, and search."""
    status = request.args.get("status")
    floor = request.args.get("floor")
    room_type_id = request.args.get("room_type_id")
    search = request.args.get("search", "").strip()

    query = """
        SELECT 
            rm.room_id,
            rm.room_number,
            rm.room_type_id,
            rm.floor,
            rm.status,
            rt.room_type,
            rt.description,
            rt.price_per_night,
            rt.capacity
        FROM Rooms rm
        JOIN Room_Types rt ON rm.room_type_id = rt.room_type_id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND rm.status = ?"
        params.append(status)
    if floor:
        query += " AND rm.floor = ?"
        params.append(floor)
    if room_type_id:
        query += " AND rm.room_type_id = ?"
        params.append(room_type_id)
    if search:
        query += " AND (rm.room_number LIKE ? OR rt.room_type LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY rm.floor ASC, rm.room_number ASC;"
    rooms = db.query_db(query, tuple(params))
    return jsonify({"success": True, "data": rooms})


@app.route("/api/rooms/available", methods=["GET"])
def get_available_rooms():
    """
    Queries rooms that are strictly available for a specific date range [check_in, check_out].
    Prevents double bookings by excluding any rooms with overlapping active reservations!
    """
    check_in = request.args.get("check_in")
    check_out = request.args.get("check_out")
    room_type_id = request.args.get("room_type_id")
    min_capacity = request.args.get("min_capacity", 1)

    if not check_in or not check_out:
        return jsonify({"success": False, "message": "Check-in and Check-out dates are required."}), 400

    if check_out <= check_in:
        return jsonify({"success": False, "message": "Check-out date must be strictly after Check-in date."}), 400

    try:
        min_capacity = int(min_capacity)
    except ValueError:
        min_capacity = 1

    available_rooms = db.get_available_rooms_for_dates(
        check_in=check_in,
        check_out=check_out,
        room_type_id=room_type_id,
        min_capacity=min_capacity
    )
    return jsonify({"success": True, "data": available_rooms, "count": len(available_rooms)})


@app.route("/api/rooms", methods=["POST"])
def create_room():
    """Adds a new hotel room."""
    data = request.get_json() or {}
    room_number = str(data.get("room_number", "")).strip()
    room_type_id = data.get("room_type_id")
    floor = data.get("floor")
    status = data.get("status", "Available")

    if not room_number:
        return jsonify({"success": False, "message": "Room number is required."}), 400
    if not room_type_id:
        return jsonify({"success": False, "message": "Room type is required."}), 400
    try:
        floor = int(floor)
        if floor < 1:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Floor must be a positive integer."}), 400

    valid_statuses = ("Available", "Occupied", "Reserved", "Maintenance")
    if status not in valid_statuses:
        return jsonify({"success": False, "message": f"Status must be one of {valid_statuses}"}), 400

    # Verify room_type_id exists (Foreign Key Check)
    rt = db.query_db("SELECT room_type_id FROM Room_Types WHERE room_type_id = ?", (room_type_id,), one=True)
    if not rt:
        return jsonify({"success": False, "message": "Selected Room Type does not exist in database."}), 400

    try:
        res = db.execute_db("""
            INSERT INTO Rooms (room_number, room_type_id, floor, status)
            VALUES (?, ?, ?, ?);
        """, (room_number, room_type_id, floor, status))
        return jsonify({
            "success": True,
            "message": f"Room {room_number} added successfully.",
            "room_id": res["last_row_id"]
        }), 201
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": f"Room number '{room_number}' already exists."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/rooms/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    """Updates an existing room."""
    data = request.get_json() or {}
    room_number = str(data.get("room_number", "")).strip()
    room_type_id = data.get("room_type_id")
    floor = data.get("floor")
    status = data.get("status")

    if not room_number or not room_type_id or floor is None or not status:
        return jsonify({"success": False, "message": "All room fields are required."}), 400

    valid_statuses = ("Available", "Occupied", "Reserved", "Maintenance")
    if status not in valid_statuses:
        return jsonify({"success": False, "message": f"Status must be one of {valid_statuses}"}), 400

    try:
        db.execute_db("""
            UPDATE Rooms 
            SET room_number = ?, room_type_id = ?, floor = ?, status = ?
            WHERE room_id = ?;
        """, (room_number, room_type_id, int(floor), status, room_id))
        return jsonify({"success": True, "message": f"Room {room_number} updated successfully."})
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": f"Room number '{room_number}' is already in use."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/rooms/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    """Deletes a room, checking for existing reservations."""
    active_res = db.query_db("""
        SELECT COUNT(*) AS count FROM Reservations 
        WHERE room_id = ? AND reservation_status IN ('Confirmed', 'Checked-In')
    """, (room_id,), one=True)
    if active_res and active_res["count"] > 0:
        return jsonify({
            "success": False,
            "message": "Cannot delete: This room has active reservations. Cancel or checkout reservations first."
        }), 409

    try:
        db.execute_db("DELETE FROM Rooms WHERE room_id = ?", (room_id,))
        return jsonify({"success": True, "message": "Room deleted successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# ==============================================================================
# 4. GUESTS CRUD & SEARCH
# ==============================================================================

@app.route("/api/guests", methods=["GET"])
def get_guests():
    """Fetches guests with reservation counts, search filter on name, email, phone."""
    search = request.args.get("search", "").strip()
    query = """
        SELECT 
            g.guest_id,
            g.guest_name,
            g.phone,
            g.email,
            g.address,
            COUNT(r.reservation_id) AS total_reservations,
            g.created_at
        FROM Guests g
        LEFT JOIN Reservations r ON g.guest_id = r.guest_id
    """
    params = []
    if search:
        query += " WHERE g.guest_name LIKE ? OR g.email LIKE ? OR g.phone LIKE ?"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " GROUP BY g.guest_id ORDER BY g.guest_id DESC;"
    guests = db.query_db(query, tuple(params))
    return jsonify({"success": True, "data": guests})


@app.route("/api/guests/<int:guest_id>", methods=["GET"])
def get_single_guest(guest_id):
    """Fetches a single guest and their full reservation and payment history."""
    guest = db.query_db("SELECT * FROM Guests WHERE guest_id = ?", (guest_id,), one=True)
    if not guest:
        return jsonify({"success": False, "message": "Guest not found."}), 404

    reservations = db.query_db("""
        SELECT 
            r.reservation_id,
            r.check_in,
            r.check_out,
            r.number_of_guests,
            r.reservation_status,
            r.total_price,
            rm.room_number,
            rt.room_type
        FROM Reservations r
        JOIN Rooms rm ON r.room_id = rm.room_id
        JOIN Room_Types rt ON rm.room_type_id = rt.room_type_id
        WHERE r.guest_id = ?
        ORDER BY r.reservation_id DESC;
    """, (guest_id,))

    return jsonify({"success": True, "data": guest, "reservations": reservations})


@app.route("/api/guests", methods=["POST"])
def create_guest():
    """Registers a new guest."""
    data = request.get_json() or {}
    guest_name = data.get("guest_name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()

    if len(guest_name) < 2:
        return jsonify({"success": False, "message": "Guest name must be at least 2 characters."}), 400
    if len(phone) < 7:
        return jsonify({"success": False, "message": "Valid phone number is required (min 7 digits)."}), 400
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    try:
        res = db.execute_db("""
            INSERT INTO Guests (guest_name, phone, email, address)
            VALUES (?, ?, ?, ?);
        """, (guest_name, phone, email, address))
        return jsonify({
            "success": True,
            "message": f"Guest '{guest_name}' registered successfully.",
            "guest_id": res["last_row_id"]
        }), 201
    except Exception as e:
        if "UNIQUE" in str(e):
            if "phone" in str(e):
                return jsonify({"success": False, "message": "A guest with this phone number already exists."}), 409
            return jsonify({"success": False, "message": "A guest with this email address already exists."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/guests/<int:guest_id>", methods=["PUT"])
def update_guest(guest_id):
    """Updates guest details."""
    data = request.get_json() or {}
    guest_name = data.get("guest_name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()

    if len(guest_name) < 2 or len(phone) < 7 or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"success": False, "message": "Please provide valid name, phone, and email."}), 400

    try:
        db.execute_db("""
            UPDATE Guests 
            SET guest_name = ?, phone = ?, email = ?, address = ?
            WHERE guest_id = ?;
        """, (guest_name, phone, email, address, guest_id))
        return jsonify({"success": True, "message": "Guest updated successfully."})
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": "Phone number or email is already registered to another guest."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/guests/<int:guest_id>", methods=["DELETE"])
def delete_guest(guest_id):
    """Deletes a guest with foreign key checks."""
    res_count = db.query_db("SELECT COUNT(*) AS count FROM Reservations WHERE guest_id = ?", (guest_id,), one=True)
    if res_count and res_count["count"] > 0:
        return jsonify({
            "success": False,
            "message": f"Cannot delete: Guest has {res_count['count']} reservation(s) on file (DBMS Foreign Key RESTRICT)."
        }), 409

    try:
        db.execute_db("DELETE FROM Guests WHERE guest_id = ?", (guest_id,))
        return jsonify({"success": True, "message": "Guest deleted successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# ==============================================================================
# 5. RESERVATIONS CRUD & AVAILABILITY LOGIC
# ==============================================================================

@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    """Fetches reservations with JOINs to Guests, Rooms, and Room_Types."""
    status = request.args.get("status")
    search = request.args.get("search", "").strip()

    query = """
        SELECT 
            r.reservation_id,
            r.guest_id,
            g.guest_name,
            g.phone AS guest_phone,
            g.email AS guest_email,
            r.room_id,
            rm.room_number,
            rm.floor,
            rt.room_type,
            rt.price_per_night,
            r.check_in,
            r.check_out,
            r.number_of_guests,
            r.reservation_status,
            r.total_price,
            r.created_at,
            p.payment_id,
            p.payment_status,
            p.payment_method,
            p.amount AS payment_amount
        FROM Reservations r
        JOIN Guests g ON r.guest_id = g.guest_id
        JOIN Rooms rm ON r.room_id = rm.room_id
        JOIN Room_Types rt ON rm.room_type_id = rt.room_type_id
        LEFT JOIN Payments p ON r.reservation_id = p.reservation_id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND r.reservation_status = ?"
        params.append(status)
    if search:
        query += " AND (g.guest_name LIKE ? OR rm.room_number LIKE ? OR r.reservation_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY r.reservation_id DESC;"
    reservations = db.query_db(query, tuple(params))
    return jsonify({"success": True, "data": reservations})


@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    """
    Processes the Make Reservation form.
    CRITICAL DBMS VALIDATIONS:
    1. Foreign Key Verification: guest_id and room_id must exist.
    2. CHECK constraint: check_out > check_in.
    3. Double Booking Prevention: Room must not be booked in the selected dates!
    4. Capacity Validation: number_of_guests <= Room_Types.capacity.
    5. Price calculation: nights * price_per_night.
    6. Automatically creates corresponding Payment record if specified.
    """
    data = request.get_json() or {}
    guest_id = data.get("guest_id")
    room_id = data.get("room_id")
    check_in = data.get("check_in")
    check_out = data.get("check_out")
    number_of_guests = data.get("number_of_guests")
    reservation_status = data.get("reservation_status", "Confirmed")
    payment_method = data.get("payment_method") # 'Cash', 'Card', 'UPI', or None
    payment_status = data.get("payment_status", "Paid")

    # Basic validations
    if not guest_id or not room_id or not check_in or not check_out or not number_of_guests:
        return jsonify({"success": False, "message": "All reservation fields are required."}), 400

    try:
        check_in_date = datetime.date.fromisoformat(check_in)
        check_out_date = datetime.date.fromisoformat(check_out)
        if check_out_date <= check_in_date:
            return jsonify({"success": False, "message": "Check-out date must be strictly after Check-in date."}), 400
        nights = (check_out_date - check_in_date).days
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        number_of_guests = int(number_of_guests)
        if number_of_guests < 1:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Number of guests must be at least 1."}), 400

    # Verify Guest existence
    guest = db.query_db("SELECT guest_id, guest_name FROM Guests WHERE guest_id = ?", (guest_id,), one=True)
    if not guest:
        return jsonify({"success": False, "message": "Guest not found in database."}), 404

    # Verify Room and Room Type capacity
    room = db.query_db("""
        SELECT rm.room_id, rm.room_number, rm.status, rt.capacity, rt.price_per_night, rt.room_type
        FROM Rooms rm
        JOIN Room_Types rt ON rm.room_type_id = rt.room_type_id
        WHERE rm.room_id = ?;
    """, (room_id,), one=True)
    if not room:
        return jsonify({"success": False, "message": "Room not found in database."}), 404

    if number_of_guests > room["capacity"]:
        return jsonify({
            "success": False, 
            "message": f"Number of guests ({number_of_guests}) exceeds {room['room_type']} capacity ({room['capacity']})."
        }), 400

    # Double Booking Prevention Validation
    is_available, error_msg = db.check_room_availability(room_id, check_in, check_out)
    if not is_available:
        return jsonify({"success": False, "message": error_msg}), 409

    # Calculate Total Price
    total_price = round(nights * room["price_per_night"], 2)

    # Perform Reservation & Payment creation in a transaction
    try:
        res = db.execute_db("""
            INSERT INTO Reservations (guest_id, room_id, check_in, check_out, number_of_guests, reservation_status, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (guest_id, room_id, check_in, check_out, number_of_guests, reservation_status, total_price))
        reservation_id = res["last_row_id"]

        # If payment details provided, insert into Payments table
        payment_id = None
        if payment_method:
            txn_ref = f"TXN-{payment_method.upper()}-{reservation_id}{datetime.datetime.now().strftime('%M%S')}"
            pay_res = db.execute_db("""
                INSERT INTO Payments (reservation_id, guest_id, amount, payment_date, payment_method, payment_status, transaction_ref)
                VALUES (?, ?, ?, date('now'), ?, ?, ?);
            """, (reservation_id, guest_id, total_price, payment_method, payment_status, txn_ref))
            payment_id = pay_res["last_row_id"]

        # Update room status if reservation is Checked-In or Confirmed for today
        today_str = datetime.date.today().isoformat()
        if reservation_status == "Checked-In":
            db.execute_db("UPDATE Rooms SET status = 'Occupied' WHERE room_id = ?", (room_id,))
        elif reservation_status == "Confirmed" and check_in <= today_str <= check_out:
            db.execute_db("UPDATE Rooms SET status = 'Reserved' WHERE room_id = ?", (room_id,))

        return jsonify({
            "success": True,
            "message": f"Reservation #{reservation_id} confirmed for {guest['guest_name']} in Room {room['room_number']}.",
            "reservation_id": reservation_id,
            "payment_id": payment_id,
            "total_price": total_price,
            "nights": nights
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": f"Database error creating reservation: {str(e)}"}), 500


@app.route("/api/reservations/<int:reservation_id>/status", methods=["PUT"])
def update_reservation_status(reservation_id):
    """Updates status of a reservation and automatically synchronizes room status."""
    data = request.get_json() or {}
    new_status = data.get("reservation_status")

    valid_statuses = ("Confirmed", "Checked-In", "Checked-Out", "Cancelled")
    if new_status not in valid_statuses:
        return jsonify({"success": False, "message": f"Invalid status. Must be one of {valid_statuses}"}), 400

    res = db.query_db("SELECT * FROM Reservations WHERE reservation_id = ?", (reservation_id,), one=True)
    if not res:
        return jsonify({"success": False, "message": "Reservation not found."}), 404

    try:
        db.execute_db("""
            UPDATE Reservations 
            SET reservation_status = ? 
            WHERE reservation_id = ?;
        """, (new_status, reservation_id))

        # Synchronize Room status based on new reservation status
        room_id = res["room_id"]
        if new_status == "Checked-In":
            db.execute_db("UPDATE Rooms SET status = 'Occupied' WHERE room_id = ?", (room_id,))
        elif new_status in ("Checked-Out", "Cancelled"):
            db.execute_db("UPDATE Rooms SET status = 'Available' WHERE room_id = ?", (room_id,))
        elif new_status == "Confirmed":
            today_str = datetime.date.today().isoformat()
            if res["check_in"] <= today_str <= res["check_out"]:
                db.execute_db("UPDATE Rooms SET status = 'Reserved' WHERE room_id = ?", (room_id,))
            else:
                db.execute_db("UPDATE Rooms SET status = 'Available' WHERE room_id = ?", (room_id,))

        return jsonify({
            "success": True, 
            "message": f"Reservation #{reservation_id} updated to '{new_status}'."
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/reservations/<int:reservation_id>", methods=["DELETE"])
def delete_reservation(reservation_id):
    """Deletes a reservation (cascades to payments as defined in schema)."""
    res = db.query_db("SELECT room_id FROM Reservations WHERE reservation_id = ?", (reservation_id,), one=True)
    if not res:
        return jsonify({"success": False, "message": "Reservation not found."}), 404

    try:
        room_id = res["room_id"]
        db.execute_db("DELETE FROM Reservations WHERE reservation_id = ?", (reservation_id,))
        # Set room back to available if no other active reservation occupies it
        db.sync_all_room_statuses()
        return jsonify({"success": True, "message": f"Reservation #{reservation_id} deleted."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# ==============================================================================
# 6. PAYMENTS CRUD & TRANSACTIONS
# ==============================================================================

@app.route("/api/payments", methods=["GET"])
def get_payments():
    """Fetches payments with JOIN to Reservations and Guests."""
    method = request.args.get("payment_method")
    status = request.args.get("payment_status")
    search = request.args.get("search", "").strip()

    query = """
        SELECT 
            p.payment_id,
            p.reservation_id,
            p.guest_id,
            g.guest_name,
            g.email AS guest_email,
            rm.room_number,
            p.amount,
            p.payment_date,
            p.payment_method,
            p.payment_status,
            p.transaction_ref,
            p.created_at
        FROM Payments p
        JOIN Guests g ON p.guest_id = g.guest_id
        JOIN Reservations r ON p.reservation_id = r.reservation_id
        JOIN Rooms rm ON r.room_id = rm.room_id
        WHERE 1=1
    """
    params = []
    if method:
        query += " AND p.payment_method = ?"
        params.append(method)
    if status:
        query += " AND p.payment_status = ?"
        params.append(status)
    if search:
        query += " AND (g.guest_name LIKE ? OR p.transaction_ref LIKE ? OR p.reservation_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY p.payment_id DESC;"
    payments = db.query_db(query, tuple(params))
    return jsonify({"success": True, "data": payments})


@app.route("/api/payments", methods=["POST"])
def create_payment():
    """Records a new payment for a reservation."""
    data = request.get_json() or {}
    reservation_id = data.get("reservation_id")
    amount = data.get("amount")
    payment_method = data.get("payment_method")
    payment_status = data.get("payment_status", "Paid")

    if not reservation_id or amount is None or not payment_method:
        return jsonify({"success": False, "message": "Reservation ID, amount, and payment method are required."}), 400

    try:
        amount = float(amount)
        if amount < 0:
            return jsonify({"success": False, "message": "Payment amount cannot be negative (CHECK constraint)."}), 400
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Amount must be a valid number."}), 400

    if payment_method not in ("Cash", "Card", "UPI"):
        return jsonify({"success": False, "message": "Payment method must be Cash, Card, or UPI."}), 400

    if payment_status not in ("Paid", "Pending", "Refunded"):
        return jsonify({"success": False, "message": "Payment status must be Paid, Pending, or Refunded."}), 400

    # Verify reservation exists and retrieve guest_id (DBMS Foreign Key)
    res = db.query_db("SELECT reservation_id, guest_id FROM Reservations WHERE reservation_id = ?", (reservation_id,), one=True)
    if not res:
        return jsonify({"success": False, "message": "Reservation not found in database."}), 404

    txn_ref = f"TXN-{payment_method.upper()}-{reservation_id}{datetime.datetime.now().strftime('%M%S')}"
    try:
        result = db.execute_db("""
            INSERT INTO Payments (reservation_id, guest_id, amount, payment_date, payment_method, payment_status, transaction_ref)
            VALUES (?, ?, ?, date('now'), ?, ?, ?);
        """, (reservation_id, res["guest_id"], amount, payment_method, payment_status, txn_ref))
        return jsonify({
            "success": True,
            "message": "Payment recorded successfully.",
            "payment_id": result["last_row_id"],
            "transaction_ref": txn_ref
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/payments/<int:payment_id>/status", methods=["PUT"])
def update_payment_status(payment_id):
    """Updates payment status (Paid, Pending, Refunded)."""
    data = request.get_json() or {}
    new_status = data.get("payment_status")

    if new_status not in ("Paid", "Pending", "Refunded"):
        return jsonify({"success": False, "message": "Status must be Paid, Pending, or Refunded."}), 400

    try:
        db.execute_db("UPDATE Payments SET payment_status = ? WHERE payment_id = ?", (new_status, payment_id))
        return jsonify({"success": True, "message": f"Payment #{payment_id} status updated to {new_status}."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/payments/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    """Deletes a payment record."""
    try:
        db.execute_db("DELETE FROM Payments WHERE payment_id = ?", (payment_id,))
        return jsonify({"success": True, "message": "Payment record deleted."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# ==============================================================================
# 7. STAFF CRUD
# ==============================================================================

@app.route("/api/staff", methods=["GET"])
def get_staff():
    """Fetches staff members with optional role filter and search."""
    role = request.args.get("role")
    search = request.args.get("search", "").strip()

    query = "SELECT * FROM Staff WHERE 1=1"
    params = []
    if role:
        query += " AND role = ?"
        params.append(role)
    if search:
        query += " AND (staff_name LIKE ? OR email LIKE ? OR phone LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY staff_id ASC;"
    staff = db.query_db(query, tuple(params))
    return jsonify({"success": True, "data": staff})


@app.route("/api/staff", methods=["POST"])
def create_staff():
    """Adds a new hotel staff member."""
    data = request.get_json() or {}
    staff_name = data.get("staff_name", "").strip()
    role = data.get("role", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()

    valid_roles = (
        'Hotel Manager', 'Front Desk Executive', 'Concierge',
        'Housekeeping Supervisor', 'Maintenance Engineer', 'Accountant', 'Executive Chef'
    )
    if len(staff_name) < 2:
        return jsonify({"success": False, "message": "Staff name is required (min 2 chars)."}), 400
    if role not in valid_roles:
        return jsonify({"success": False, "message": f"Invalid role. Must be one of: {', '.join(valid_roles)}"}), 400
    if len(phone) < 7:
        return jsonify({"success": False, "message": "Phone number is required."}), 400
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"success": False, "message": "Valid email address is required."}), 400

    try:
        res = db.execute_db("""
            INSERT INTO Staff (staff_name, role, phone, email)
            VALUES (?, ?, ?, ?);
        """, (staff_name, role, phone, email))
        return jsonify({
            "success": True,
            "message": f"Staff member '{staff_name}' added successfully.",
            "staff_id": res["last_row_id"]
        }), 201
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": "A staff member with this email already exists."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/staff/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    """Updates a staff member's info."""
    data = request.get_json() or {}
    staff_name = data.get("staff_name", "").strip()
    role = data.get("role", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()

    if len(staff_name) < 2 or not role or not phone or not email:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    try:
        db.execute_db("""
            UPDATE Staff 
            SET staff_name = ?, role = ?, phone = ?, email = ?
            WHERE staff_id = ?;
        """, (staff_name, role, phone, email, staff_id))
        return jsonify({"success": True, "message": "Staff member updated successfully."})
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": "Email already in use."}), 409
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@app.route("/api/staff/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    """Deletes a staff member."""
    try:
        db.execute_db("DELETE FROM Staff WHERE staff_id = ?", (staff_id,))
        return jsonify({"success": True, "message": "Staff member removed successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# ==============================================================================
# 8. DBMS EDUCATIONAL EXPLORER & QUERY SHOWCASE API
# ==============================================================================

@app.route("/api/dbms/schema", methods=["GET"])
def get_dbms_schema():
    """
    Returns database schema information, table structures, foreign keys,
    and constraints for academic presentation.
    """
    tables = ["Room_Types", "Rooms", "Guests", "Staff", "Reservations", "Payments"]
    schema_info = []

    for table in tables:
        columns = db.query_db(f"PRAGMA table_info({table});")
        foreign_keys = db.query_db(f"PRAGMA foreign_key_list({table});")
        row_count = db.query_db(f"SELECT COUNT(*) AS count FROM {table};", one=True)["count"]

        schema_info.append({
            "table_name": table,
            "row_count": row_count,
            "columns": columns,
            "foreign_keys": foreign_keys
        })

    return jsonify({"success": True, "tables": schema_info})


@app.route("/api/dbms/reset", methods=["POST"])
def reset_database():
    """Resets database back to clean sample data."""
    try:
        db.init_db(force_reset=True)
        return jsonify({"success": True, "message": "Database reset to initial sample data successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to reset: {str(e)}"}), 500


# ------------------------------------------------------------------------------
# APPLICATION ENTRYPOINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure database is initialized before serving requests
    db.init_db()
    print("====================================================================")
    print("  GRAND HORIZON HOTEL RESERVATION MANAGEMENT SYSTEM")
    print("  Academic DBMS Full-Stack Web Application")
    print("  URL: http://127.0.0.1:5000")
    print("====================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
