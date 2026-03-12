import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
  if (tokens.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

// Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tokens');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (data) => api.post('/auth/login', data);
export const register = (data) => api.post('/auth/register', data);
export const getProfile = () => api.get('/auth/profile');
export const updateProfile = (data) => api.patch('/auth/profile', data);

// Complaints
export const getComplaints = (params) => api.get('/complaints', { params });
export const createComplaint = (data) => api.post('/complaints', data);
export const getComplaint = (id) => api.get(`/complaints/${id}`);
export const updateComplaint = (id, data) => api.patch(`/complaints/${id}`, data);

// AI
export const predictCategory = (text) => api.post('/predict-category', { text });
export const detectDuplicate = (text) => api.post('/detect-duplicate', { text });

// Dashboard
export const getDashboardStats = () => api.get('/dashboard-stats');
export const getRootCause = () => api.get('/root-cause');
export const getRSI = () => api.get('/rsi');
export const getMaintenancePredictions = () => api.get('/maintenance-predictions');

// Feedback
export const getFeedback = () => api.get('/feedback');
export const submitFeedback = (data) => api.post('/feedback', data);

// Notifications
export const getNotifications = (unread) =>
  api.get('/notifications', { params: unread ? { unread: true } : {} });
export const markNotificationRead = (id) => api.post(`/notifications/${id}/read`);
export const markAllNotificationsRead = () => api.post('/notifications/mark-all-read');

// Technicians
export const getTechnicians = () => api.get('/technicians');
export const createTechnician = (data) => api.post('/technicians', data);
export const updateTechnician = (id, data) => api.patch(`/technicians/${id}`, data);
export const deleteTechnician = (id) => api.delete(`/technicians/${id}`);

// Assign technician to complaint
export const assignTechnician = (complaintId, technicianId) =>
  api.post(`/complaints/${complaintId}/assign`, { technician_id: technicianId });

export default api;
