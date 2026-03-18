/**
 * Auth helpers — shared across all pages.
 */
const Auth = {
  getUser() {
    try { return JSON.parse(localStorage.getItem('nexus_user')); } catch { return null; }
  },

  getToken() {
    return localStorage.getItem('nexus_token');
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  save(token, user) {
    localStorage.setItem('nexus_token', token);
    localStorage.setItem('nexus_user', JSON.stringify(user));
  },

  clear() {
    localStorage.removeItem('nexus_token');
    localStorage.removeItem('nexus_user');
  },

  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = '/index.html';
      return false;
    }
    return true;
  },

  requireRole(...roles) {
    if (!this.requireAuth()) return false;
    const user = this.getUser();
    if (!user || !roles.includes(user.role)) {
      window.location.href = '/dashboard.html';
      return false;
    }
    return true;
  },

  async logout() {
    try { await api.logout(); } catch {}
    this.clear();
    window.location.href = '/index.html';
  },
};

/** Populate sidebar user info */
function initSidebar() {
  const user = Auth.getUser();
  if (!user) return;

  const nameEl = document.getElementById('sidebar-user-name');
  const roleEl = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');

  if (nameEl) nameEl.textContent = user.full_name;
  if (roleEl) roleEl.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
  if (avatarEl) avatarEl.textContent = user.full_name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();

  // Highlight active nav
  const links = document.querySelectorAll('.nav-item');
  links.forEach(link => {
    if (link.href && window.location.href.includes(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });

  // Logout button
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', () => Auth.logout());

  // Show admin nav if admin
  if (user.role === 'admin') {
    document.querySelectorAll('[data-role="admin"]').forEach(el => el.style.display = '');
  }
  if (user.role === 'doctor') {
    document.querySelectorAll('[data-role="doctor"]').forEach(el => el.style.display = '');
  }
}

/** Format ISO date for display */
function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
  });
}

/** Status badge HTML */
function statusBadge(status) {
  return `<span class="badge badge-${status}">${status}</span>`;
}

/** Role badge HTML */
function roleBadge(role) {
  return `<span class="badge badge-${role}">${role}</span>`;
}

/** Show an alert inside a container */
function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
}
