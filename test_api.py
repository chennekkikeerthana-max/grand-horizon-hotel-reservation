"""
Verification test script for Hotel Reservation Management System REST API.
"""
import app
import json

def run_tests():
    client = app.app.test_client()
    
    print("Testing 1: Dashboard stats...")
    r = client.get('/api/dashboard/stats')
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.get_json()
    assert data["success"] is True
    print(f"  Rooms total: {data['rooms']['total_rooms']}, Guests: {data['guests']}, Revenue: ${data['revenue']['total_revenue']}")
    
    print("Testing 2: Reports analytics...")
    r = client.get('/api/reports/analytics')
    assert r.status_code == 200
    rep = r.get_json()
    assert rep["success"] is True
    print(f"  Occupancy rate: {rep['aggregates']['occupancy_rate']}%")
    print(f"  Popular room types count: {len(rep['room_type_popularity'])}")
    
    print("Testing 3: Room types listing & creation...")
    r = client.get('/api/room-types')
    assert r.status_code == 200
    r_types = r.get_json()["data"]
    print(f"  Existing room types: {len(r_types)}")
    
    print("Testing 4: Rooms list & availability check...")
    r = client.get('/api/rooms')
    assert r.status_code == 200
    rooms = r.get_json()["data"]
    print(f"  Total rooms retrieved: {len(rooms)}")
    
    # Check availability for dates
    r = client.get('/api/rooms/available?check_in=2026-11-01&check_out=2026-11-05&min_capacity=2')
    assert r.status_code == 200
    avail = r.get_json()
    print(f"  Available rooms for 2026-11-01 to 2026-11-05: {avail['count']}")
    
    print("Testing 5: Double-booking prevention check...")
    # Room 102 is currently booked from 2026-09-30 to 2026-10-04 (Checked-In).
    # Trying to book Room 102 from 2026-10-02 to 2026-10-06 should be REJECTED!
    new_res_payload = {
        "guest_id": 1,
        "room_id": 102,
        "check_in": "2026-10-02",
        "check_out": "2026-10-06",
        "number_of_guests": 2,
        "reservation_status": "Confirmed",
        "payment_method": "Card"
    }
    r = client.post('/api/reservations', json=new_res_payload)
    assert r.status_code == 409, f"Expected 409 Conflict for double booking, got {r.status_code}: {r.get_json()}"
    print(f"  Double booking correctly rejected: {r.get_json()['message']}")

    print("Testing 6: Valid reservation creation...")
    # Room 101 is available in November
    valid_res_payload = {
        "guest_id": 2,
        "room_id": 101,
        "check_in": "2026-11-10",
        "check_out": "2026-11-14",
        "number_of_guests": 2,
        "reservation_status": "Confirmed",
        "payment_method": "UPI",
        "payment_status": "Paid"
    }
    r = client.post('/api/reservations', json=valid_res_payload)
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.get_json()}"
    res_data = r.get_json()
    new_res_id = res_data["reservation_id"]
    print(f"  Created reservation #{new_res_id}, Total: ${res_data['total_price']}, Payment #{res_data['payment_id']}")

    print("Testing 7: Date check validation (check_out <= check_in)...")
    invalid_dates_payload = {
        "guest_id": 2,
        "room_id": 101,
        "check_in": "2026-11-20",
        "check_out": "2026-11-15",
        "number_of_guests": 1
    }
    r = client.post('/api/reservations', json=invalid_dates_payload)
    assert r.status_code == 400
    print(f"  Invalid dates rejected correctly: {r.get_json()['message']}")

    print("Testing 8: Capacity validation...")
    overcap_payload = {
        "guest_id": 2,
        "room_id": 101, # Standard Double capacity is 2
        "check_in": "2026-11-20",
        "check_out": "2026-11-25",
        "number_of_guests": 6
    }
    r = client.post('/api/reservations', json=overcap_payload)
    assert r.status_code == 400
    print(f"  Capacity excess rejected correctly: {r.get_json()['message']}")

    print("Testing 9: Clean up test reservation...")
    r = client.delete(f'/api/reservations/{new_res_id}')
    assert r.status_code == 200
    print(f"  Cleaned up reservation #{new_res_id}")

    print("Testing 10: DBMS Schema Info...")
    r = client.get('/api/dbms/schema')
    assert r.status_code == 200
    schema = r.get_json()["tables"]
    print(f"  Verified {len(schema)} database tables in schema explorer.")

    print("\nALL 10 API & DATABASE INTEGRITY TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
