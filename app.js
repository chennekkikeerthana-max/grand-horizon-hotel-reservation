/**
 * ============================================================================
 * GRAND HORIZON HOTEL RESERVATION MANAGEMENT SYSTEM - CORE APP CONTROLLER
 * Router, Modal Manager, Toast Alerts, and Global State Synchronization
 * ============================================================================
 */

// Utility: XSS prevention
function escapeHtml(unsafe) {
  if (unsafe === null || unsafe === undefined) return '';
  return String(unsafe)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

const App = {
  currentPage: 'dashboard',

  init() {
    console.log('[Grand Horizon HMS] Initializing full-stack application...');

    // Setup navigation listeners
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.getAttribute('data-page');
        if (page) {
          this.navigateTo(page);
          // Close mobile menu if open
          document.querySelector('.sidebar').classList.remove('mobile-open');
        }
      });
    });

    // Mobile menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
      menuToggle.addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('mobile-open');
      });
    }

    // Modal background click to close
    const modalOverlay = document.getElementById('app-modal');
    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
          this.closeModal();
        }
      });
    }

    // Keyboard shortcuts (Escape closes modal)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeModal();
      }
    });

    // Initial page route
    const hash = window.location.hash.replace('#', '');
    const validPages = ['dashboard', 'room-types', 'rooms', 'guests', 'reservations', 'payments', 'staff', 'reports', 'dbms'];
    const startPage = validPages.includes(hash) ? hash : 'dashboard';
    this.navigateTo(startPage);
  },

  navigateTo(page) {
    this.currentPage = page;
    window.location.hash = page;

    // Update Sidebar Active Class
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.getAttribute('data-page') === page) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Toggle Content Views
    document.querySelectorAll('.page-view').forEach(view => {
      view.classList.remove('active');
    });

    const targetView = document.getElementById(`view-${page}`);
    if (targetView) {
      targetView.classList.add('active');
    }

    // Update Topbar Title
    this.updateHeaderTitle(page);

    // Render Component
    switch (page) {
      case 'dashboard':
        DashboardComponent.render();
        break;
      case 'room-types':
        RoomTypesComponent.render();
        break;
      case 'rooms':
        RoomsComponent.render();
        break;
      case 'guests':
        GuestsComponent.render();
        break;
      case 'reservations':
        ReservationsComponent.render();
        break;
      case 'payments':
        PaymentsComponent.render();
        break;
      case 'staff':
        StaffComponent.render();
        break;
      case 'reports':
        ReportsComponent.render();
        break;
      case 'dbms':
        DbmsExplorerComponent.render();
        break;
      default:
        DashboardComponent.render();
    }
  },

  updateHeaderTitle(page) {
    const titleMap = {
      'dashboard': { title: 'Executive Overview', desc: 'Real-time hotel occupancy, reservation analytics, and operational metrics' },
      'room-types': { title: 'Room Types & Suites', desc: 'Category configuration, nightly rates, and capacity parameters' },
      'rooms': { title: 'Rooms Management', desc: 'Floor plans, room status tracking, and housekeeping allocations' },
      'guests': { title: 'Guests Directory', desc: 'Guest profile database, contact records, and historical stays' },
      'reservations': { title: 'Reservations Desk', desc: 'Active bookings, check-in/out workflows, and automated availability' },
      'payments': { title: 'Billing & Transactions', desc: 'Payment logging, settlement methods (Cash, Card, UPI), and folios' },
      'staff': { title: 'Staff Directory', desc: 'Employee records, operational roles, and system contacts' },
      'reports': { title: 'Analytics & Reports', desc: 'DBMS aggregate queries, revenue trends, and occupancy distributions' },
      'dbms': { title: 'DBMS Relational Architecture', desc: 'Keys, constraints, ER diagram, and live SQL statements' }
    };

    const info = titleMap[page] || titleMap['dashboard'];
    document.getElementById('header-page-title').textContent = info.title;
    document.getElementById('header-page-subtitle').textContent = info.desc;
  },

  // Modal Manager
  openModal(contentHtml, isLarge = false) {
    const overlay = document.getElementById('app-modal');
    const container = document.getElementById('modal-inner-container');
    if (!overlay || !container) return;

    if (isLarge) {
      container.classList.add('modal-lg');
    } else {
      container.classList.remove('modal-lg');
    }

    container.innerHTML = contentHtml;
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  },

  closeModal() {
    const overlay = document.getElementById('app-modal');
    if (overlay) {
      overlay.classList.remove('active');
    }
    document.body.style.overflow = '';
  },

  // Toast Notification System
  showToast(title, message, type = 'info') {
    let container = document.getElementById('app-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'app-toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    else if (type === 'error') icon = 'fa-circle-exclamation';
    else if (type === 'warning') icon = 'fa-triangle-exclamation';

    toast.innerHTML = `
      <i class="fa-solid ${icon}" style="font-size: 18px; margin-top: 2px;"></i>
      <div class="toast-content">
        <div class="toast-title">${escapeHtml(title)}</div>
        <div class="toast-message">${escapeHtml(message)}</div>
      </div>
      <button style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:14px;" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s, transform 0.3s';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(50px)';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  },

  // Reset database confirmation modal
  confirmResetDatabase() {
    this.openModal(`
      <div class="modal-header" style="background: #fef2f2;">
        <h3 style="color: #b91c1c;"><i class="fa-solid fa-triangle-exclamation"></i> Reset Database to Clean Seed Data</h3>
        <button class="modal-close-btn" onclick="App.closeModal()">&times;</button>
      </div>
      <div class="modal-body">
        <p style="margin-bottom: 12px; font-weight: 600;">
          Are you sure you want to reset the entire database?
        </p>
        <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 12px;">
          This will execute <code>schema.sql</code> and re-populate the original realistic seed data (5 room types, 16 rooms, 10 guests, 8 staff, 10 reservations, 10 payments).
        </p>
        <div class="sql-viewer-box">
          -- DBMS Initialization Script:
          DROP TABLE IF EXISTS Payments;
          DROP TABLE IF EXISTS Reservations;
          ...
          -- Re-creates tables, indexes, triggers and runs seed.sql
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
        <button class="btn btn-danger" onclick="App.executeResetDatabase()">
          <i class="fa-solid fa-rotate-left"></i> Confirm Reset
        </button>
      </div>
    `);
  },

  async executeResetDatabase() {
    try {
      const res = await API.resetDatabase();
      this.closeModal();
      this.showToast('Database Reset', res.message, 'success');
      this.navigateTo(this.currentPage);
    } catch (err) {
      this.showToast('Reset Failed', err.message, 'error');
    }
  }
};

// Start application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
