/**
 * ============================================================================
 * GRAND HORIZON HOTEL RESERVATION MANAGEMENT SYSTEM - API CLIENT
 * Encapsulates all REST API calls with error handling
 * ============================================================================
 */

const API = {
  // Base request helper
  async request(endpoint, options = {}) {
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(endpoint, config);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || `HTTP Error ${response.status}`);
      }
      return data;
    } catch (error) {
      console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, error);
      throw error;
    }
  },

  // 1. Dashboard & Reports
  async getDashboardStats() {
    return this.request('/api/dashboard/stats');
  },

  async getReportsAnalytics() {
    return this.request('/api/reports/analytics');
  },

  // 2. Room Types
  async getRoomTypes(search = '') {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request(`/api/room-types${query}`);
  },

  async getRoomType(id) {
    return this.request(`/api/room-types/${id}`);
  },

  async createRoomType(payload) {
    return this.request('/api/room-types', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateRoomType(id, payload) {
    return this.request(`/api/room-types/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteRoomType(id) {
    return this.request(`/api/room-types/${id}`, {
      method: 'DELETE'
    });
  },

  // 3. Rooms
  async getRooms(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.floor) params.append('floor', filters.floor);
    if (filters.room_type_id) params.append('room_type_id', filters.room_type_id);
    if (filters.search) params.append('search', filters.search);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request(`/api/rooms${queryString}`);
  },

  async getAvailableRooms(checkIn, checkOut, roomTypeId = null, minCapacity = 1) {
    const params = new URLSearchParams({
      check_in: checkIn,
      check_out: checkOut,
      min_capacity: minCapacity
    });
    if (roomTypeId) params.append('room_type_id', roomTypeId);
    return this.request(`/api/rooms/available?${params.toString()}`);
  },

  async createRoom(payload) {
    return this.request('/api/rooms', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateRoom(id, payload) {
    return this.request(`/api/rooms/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteRoom(id) {
    return this.request(`/api/rooms/${id}`, {
      method: 'DELETE'
    });
  },

  // 4. Guests
  async getGuests(search = '') {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request(`/api/guests${query}`);
  },

  async getGuest(id) {
    return this.request(`/api/guests/${id}`);
  },

  async createGuest(payload) {
    return this.request('/api/guests', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateGuest(id, payload) {
    return this.request(`/api/guests/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteGuest(id) {
    return this.request(`/api/guests/${id}`, {
      method: 'DELETE'
    });
  },

  // 5. Reservations
  async getReservations(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request(`/api/reservations${queryString}`);
  },

  async createReservation(payload) {
    return this.request('/api/reservations', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateReservationStatus(id, status) {
    return this.request(`/api/reservations/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ reservation_status: status })
    });
  },

  async deleteReservation(id) {
    return this.request(`/api/reservations/${id}`, {
      method: 'DELETE'
    });
  },

  // 6. Payments
  async getPayments(filters = {}) {
    const params = new URLSearchParams();
    if (filters.payment_method) params.append('payment_method', filters.payment_method);
    if (filters.payment_status) params.append('payment_status', filters.payment_status);
    if (filters.search) params.append('search', filters.search);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request(`/api/payments${queryString}`);
  },

  async createPayment(payload) {
    return this.request('/api/payments', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updatePaymentStatus(id, status) {
    return this.request(`/api/payments/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ payment_status: status })
    });
  },

  async deletePayment(id) {
    return this.request(`/api/payments/${id}`, {
      method: 'DELETE'
    });
  },

  // 7. Staff
  async getStaff(filters = {}) {
    const params = new URLSearchParams();
    if (filters.role) params.append('role', filters.role);
    if (filters.search) params.append('search', filters.search);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request(`/api/staff${queryString}`);
  },

  async createStaff(payload) {
    return this.request('/api/staff', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateStaff(id, payload) {
    return this.request(`/api/staff/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteStaff(id) {
    return this.request(`/api/staff/${id}`, {
      method: 'DELETE'
    });
  },

  // 8. DBMS Explorer & Reset
  async getDbmsSchema() {
    return this.request('/api/dbms/schema');
  },

  async resetDatabase() {
    return this.request('/api/dbms/reset', {
      method: 'POST'
    });
  }
};
