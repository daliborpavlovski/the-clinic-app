/**
 * The Clinic App API client — thin wrapper around fetch.
 */
const API_BASE = window.CLINIC_API_URL || '/api/v1';

const api = {
  _getToken() {
    return localStorage.getItem('clinic_token');
  },

  _headers(extra = {}) {
    const h = { 'Content-Type': 'application/json', ...extra };
    const token = this._getToken();
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
  },

  async _fetch(method, path, body) {
    const opts = { method, headers: this._headers() };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);

    let data;
    try { data = await res.json(); } catch { data = null; }

    if (res.status === 401) {
      const msg = data?.detail || 'Unauthorized';
      // Redirect to login only for token-expiry on authenticated pages
      if (!window.location.pathname.includes('index.html') && window.location.pathname !== '/') {
        localStorage.removeItem('clinic_token');
        localStorage.removeItem('clinic_user');
        window.location.href = '/index.html';
      }
      throw Object.assign(new Error(msg), { status: 401, data });
    }

    if (!res.ok) {
      const msg = data?.detail || `HTTP ${res.status}`;
      throw Object.assign(new Error(msg), { status: res.status, data });
    }
    return data;
  },

  get: (path) => api._fetch('GET', path),
  post: (path, body) => api._fetch('POST', path, body),
  put: (path, body) => api._fetch('PUT', path, body),
  patch: (path, body) => api._fetch('PATCH', path, body),
  delete: (path) => api._fetch('DELETE', path),

  // Auth
  login: (email, password) => api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout', {}),
  register: (payload) => api.post('/auth/register', payload),

  // Users
  getMe: () => api.get('/users/me'),
  updateMe: (payload) => api.put('/users/me', payload),
  listUsers: (page = 1, size = 20) => api.get(`/users?page=${page}&size=${size}`),
  deleteUser: (id) => api.delete(`/users/${id}`),

  // Appointments
  listAppointments: (page = 1, size = 20) => api.get(`/appointments?page=${page}&size=${size}`),
  createAppointment: (payload) => api.post('/appointments', payload),
  getAppointment: (id) => api.get(`/appointments/${id}`),
  updateAppointment: (id, payload) => api.put(`/appointments/${id}`, payload),
  deleteAppointment: (id) => api.delete(`/appointments/${id}`),
  updateStatus: (id, status) => api.patch(`/appointments/${id}/status`, { status }),

  // Doctors
  listDoctors: (page = 1, size = 20) => api.get(`/doctors?page=${page}&size=${size}`),
  getDoctor: (id) => api.get(`/doctors/${id}`),
  getDoctorSlots: (id, from, to) => {
    const params = new URLSearchParams();
    if (from) params.set('from_date', from);
    if (to) params.set('to_date', to);
    return api.get(`/doctors/${id}/slots?${params}`);
  },
  updateDoctorProfile: (id, payload) => api.put(`/doctors/${id}/profile`, payload),
};