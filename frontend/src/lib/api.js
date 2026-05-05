import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Leads ────────────────────────────────────────────────────
export const createLead = (data) => api.post('/leads/new', data).then(r => r.data);
export const getLeads = (params) => api.get('/leads', { params }).then(r => r.data);
export const getLead = (id) => api.get(`/leads/${id}`).then(r => r.data);
export const seedDemoLeads = () => api.post('/leads/demo/seed').then(r => r.data);

// ── Calls ────────────────────────────────────────────────────
export const getCalls = (params) => api.get('/calls', { params }).then(r => r.data);
export const getCallDetail = (id) => api.get(`/calls/${id}`).then(r => r.data);

// ── Dashboard ────────────────────────────────────────────────
export const getDashboardStats = () => api.get('/dashboard/stats').then(r => r.data);
export const getRmQueue = () => api.get('/dashboard/rm-queue').then(r => r.data);
export const updateRmStatus = (id, status) =>
  api.put(`/dashboard/rm-queue/${id}/status`, null, { params: { status } }).then(r => r.data);

// ── Health ───────────────────────────────────────────────────
export const getHealth = () => api.get('/health').then(r => r.data);

export default api;
