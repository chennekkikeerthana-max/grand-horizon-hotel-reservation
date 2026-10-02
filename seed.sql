-- ============================================================================
-- HOTEL RESERVATION MANAGEMENT SYSTEM - REALISTIC SEED DATA
-- Academic DBMS Demonstration Dataset
-- ============================================================================

-- 1. SEED ROOM TYPES
INSERT OR IGNORE INTO Room_Types (room_type_id, room_type, description, price_per_night, capacity) VALUES
(1, 'Standard Double', 'Comfortable queen-bed room with city view, ergonomic work desk, high-speed WiFi, and rainfall shower.', 120.00, 2),
(2, 'Deluxe King Suite', 'Spacious king-bed suite with private balcony, mini-bar, luxury marble bathroom, and 55-inch smart TV.', 220.00, 3),
(3, 'Executive Business Suite', 'Premium suite tailored for professionals with dedicated workspace, lounge access, printer, and skyline view.', 340.00, 2),
(4, 'Family Luxury Suite', 'Two-bedroom interconnected suite with king and twin beds, kitchenette, and dedicated dining corner.', 420.00, 5),
(5, 'Presidential Royal Suite', 'Ultra-luxurious top-floor suite with master bedroom, private jacuzzi, butler service, and panoramic terrace.', 750.00, 4);

-- 2. SEED ROOMS (Floors 1 - 4)
INSERT OR IGNORE INTO Rooms (room_id, room_number, room_type_id, floor, status) VALUES
(101, '101', 1, 1, 'Available'),
(102, '102', 1, 1, 'Occupied'),
(103, '103', 1, 1, 'Available'),
(104, '104', 1, 1, 'Maintenance'),
(201, '201', 2, 2, 'Occupied'),
(202, '202', 2, 2, 'Available'),
(203, '203', 2, 2, 'Reserved'),
(204, '204', 2, 2, 'Available'),
(301, '301', 3, 3, 'Available'),
(302, '302', 3, 3, 'Occupied'),
(303, '303', 3, 3, 'Available'),
(304, '304', 4, 3, 'Available'),
(401, '401', 4, 4, 'Occupied'),
(402, '402', 4, 4, 'Available'),
(403, '403', 5, 4, 'Reserved'),
(404, '404', 5, 4, 'Available');

-- 3. SEED GUESTS
INSERT OR IGNORE INTO Guests (guest_id, guest_name, phone, email, address) VALUES
(1, 'Eleanor Vance', '+1-555-0192', 'eleanor.vance@example.com', '742 Evergreen Terrace, Springfield'),
(2, 'Marcus Thorne', '+1-555-0284', 'm.thorne@globalfinance.org', '18 Wall Street, New York, NY'),
(3, 'Dr. Samantha Reed', '+1-555-0371', 'dr.reed@hopkinshealth.edu', '302 Charles Street, Baltimore, MD'),
(4, 'Arjun Mehta', '+91-98765-43210', 'arjun.mehta@techinnovations.in', '45 Indiranagar 100ft Rd, Bengaluru'),
(5, 'Clara Dupont', '+33-1-4268-5501', 'clara.dupont@atelierparis.fr', '12 Rue de Rivoli, Paris, France'),
(6, 'David Chen', '+1-555-0819', 'david.chen@pacificventures.com', '500 Howard Street, San Francisco, CA'),
(7, 'Amina Al-Mansoor', '+971-4-321-9876', 'amina.mansoor@emiratesgroup.ae', 'Al Wasl Road, Jumeirah, Dubai'),
(8, 'Liam O''Connor', '+353-1-496-0123', 'liam.oconnor@dublinconsult.ie', '24 Grafton Street, Dublin, Ireland'),
(9, 'Sophie Martinez', '+1-555-0943', 'sophie.m@creativemedia.co', '88 Sunset Blvd, Los Angeles, CA'),
(10, 'Kenji Takahashi', '+81-3-5555-0144', 'kenji.takahashi@tokyotech.jp', 'Chiyoda-ku, Tokyo, Japan');

-- 4. SEED STAFF
INSERT OR IGNORE INTO Staff (staff_id, staff_name, role, phone, email) VALUES
(1, 'Victoria Sterling', 'Hotel Manager', '+1-555-1001', 'victoria.manager@grandhorizon.com'),
(2, 'Julian Ramirez', 'Front Desk Executive', '+1-555-1002', 'julian.frontdesk@grandhorizon.com'),
(3, 'Hannah Schmidt', 'Front Desk Executive', '+1-555-1003', 'hannah.reception@grandhorizon.com'),
(4, 'Mateo Rossi', 'Concierge', '+1-555-1004', 'mateo.concierge@grandhorizon.com'),
(5, 'Grace Montgomery', 'Housekeeping Supervisor', '+1-555-1005', 'grace.housekeeping@grandhorizon.com'),
(6, 'Vikram Patel', 'Maintenance Engineer', '+1-555-1006', 'vikram.maintenance@grandhorizon.com'),
(7, 'Catherine Tremblay', 'Accountant', '+1-555-1007', 'catherine.finance@grandhorizon.com'),
(8, 'Chef Laurent Dubois', 'Executive Chef', '+1-555-1008', 'laurent.culinary@grandhorizon.com');

-- 5. SEED RESERVATIONS
-- Note: Check dates are formatted YYYY-MM-DD
INSERT OR IGNORE INTO Reservations (reservation_id, guest_id, room_id, check_in, check_out, number_of_guests, reservation_status, total_price) VALUES
(1001, 1, 102, '2026-09-30', '2026-10-04', 2, 'Checked-In', 480.00),
(1002, 2, 201, '2026-10-01', '2026-10-05', 2, 'Checked-In', 880.00),
(1003, 3, 302, '2026-09-29', '2026-10-03', 1, 'Checked-In', 1360.00),
(1004, 4, 401, '2026-10-01', '2026-10-06', 4, 'Checked-In', 2100.00),
(1005, 5, 203, '2026-10-05', '2026-10-08', 2, 'Confirmed', 660.00),
(1006, 6, 403, '2026-10-07', '2026-10-12', 3, 'Confirmed', 3750.00),
(1007, 7, 101, '2026-09-20', '2026-09-24', 2, 'Checked-Out', 480.00),
(1008, 8, 204, '2026-09-22', '2026-09-26', 1, 'Checked-Out', 880.00),
(1009, 9, 301, '2026-09-25', '2026-09-28', 2, 'Checked-Out', 1020.00),
(1010, 10, 103, '2026-09-18', '2026-09-20', 1, 'Cancelled', 240.00);

-- 6. SEED PAYMENTS
INSERT OR IGNORE INTO Payments (payment_id, reservation_id, guest_id, amount, payment_date, payment_method, payment_status, transaction_ref) VALUES
(5001, 1001, 1, 480.00, '2026-09-30', 'Card', 'Paid', 'TXN-CARD-90214'),
(5002, 1002, 2, 880.00, '2026-10-01', 'Card', 'Paid', 'TXN-CARD-90215'),
(5003, 1003, 3, 1360.00, '2026-09-29', 'UPI', 'Paid', 'TXN-UPI-4819230'),
(5004, 1004, 4, 2100.00, '2026-10-01', 'UPI', 'Paid', 'TXN-UPI-9921402'),
(5005, 1005, 5, 660.00, '2026-10-02', 'Card', 'Paid', 'TXN-CARD-90216'),
(5006, 1006, 6, 1000.00, '2026-10-02', 'Card', 'Pending', 'TXN-PENDING-1006'),
(5007, 1007, 7, 480.00, '2026-09-20', 'Cash', 'Paid', 'TXN-CASH-7712'),
(5008, 1008, 8, 880.00, '2026-09-22', 'Card', 'Paid', 'TXN-CARD-88192'),
(5009, 1009, 9, 1020.00, '2026-09-25', 'UPI', 'Paid', 'TXN-UPI-771920'),
(5010, 1010, 10, 240.00, '2026-09-18', 'Card', 'Refunded', 'TXN-REFUND-0012');
