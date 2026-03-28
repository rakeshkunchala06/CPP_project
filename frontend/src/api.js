const API_BASE = import.meta.env.VITE_API_URL || '';

function getToken() {
  return localStorage.getItem('token');
}

function setToken(token) {
  localStorage.setItem('token', token);
}

function clearToken() {
  localStorage.removeItem('token');
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

function clearUser() {
  localStorage.removeItem('user');
}

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(url, { ...options, headers });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || 'Request failed');
  }
  return data;
}

const api = {
  // Auth
  register: (body) => request('/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/login', { method: 'POST', body: JSON.stringify(body) }),

  // Stops
  getStops: () => request('/stops'),
  createStop: (body) => request('/stops', { method: 'POST', body: JSON.stringify(body) }),
  getStop: (id) => request(`/stops/${id}`),
  updateStop: (id, body) => request(`/stops/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteStop: (id) => request(`/stops/${id}`, { method: 'DELETE' }),

  // Routes
  getRoutes: () => request('/routes'),
  createRoute: (body) => request('/routes', { method: 'POST', body: JSON.stringify(body) }),
  getRoute: (id) => request(`/routes/${id}`),
  updateRoute: (id, body) => request(`/routes/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteRoute: (id) => request(`/routes/${id}`, { method: 'DELETE' }),

  // Search
  search: (body) => request('/search', { method: 'POST', body: JSON.stringify(body) }),

  // Favorites
  addFavorite: (body) => request('/favorites', { method: 'POST', body: JSON.stringify(body) }),
  getFavorites: () => request('/favorites'),
  removeFavorite: (id) => request(`/favorites/${id}`, { method: 'DELETE' }),

  // Dashboard
  getDashboard: () => request('/dashboard'),

  // Notifications
  subscribe: (body) => request('/subscribe', { method: 'POST', body: JSON.stringify(body) }),
  getSubscribers: () => request('/subscribers'),
};

export { api, getToken, setToken, clearToken, getUser, setUser, clearUser };
export default api;
