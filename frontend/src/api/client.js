import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor to add auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return client(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => client.post('/auth/login/', credentials),
  register: (data) => client.post('/auth/register/', data),
  getMe: () => client.get('/auth/me/'),
  updateProfile: (data) => client.patch('/auth/profile/', data),
  changePassword: (data) => client.post('/auth/change-password/', data),
};

// Candidates API
export const candidatesAPI = {
  list: (params) => client.get('/candidates/', { params }),
  get: (id) => client.get(`/candidates/${id}/`),
  create: (data) => client.post('/candidates/', data),
  update: (id, data) => client.patch(`/candidates/${id}/`, data),
  delete: (id) => client.delete(`/candidates/${id}/`),
  advanceStage: (id, data) => client.post(`/candidates/${id}/advance_stage/`, data),
  uploadResume: (id, formData) =>
    client.post(`/candidates/${id}/upload_resume/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  bulkAction: (data) => client.post('/candidates/bulk_action/', data),
};

// Jobs API
export const jobsAPI = {
  list: (params) => client.get('/jobs/', { params }),
  get: (id) => client.get(`/jobs/${id}/`),
  create: (data) => client.post('/jobs/', data),
  update: (id, data) => client.patch(`/jobs/${id}/`, data),
  delete: (id) => client.delete(`/jobs/${id}/`),
  publish: (id) => client.post(`/jobs/${id}/publish/`),
  close: (id) => client.post(`/jobs/${id}/close/`),
};

// Applications API
export const applicationsAPI = {
  list: (params) => client.get('/applications/', { params }),
  get: (id) => client.get(`/applications/${id}/`),
  create: (data) => client.post('/applications/', data),
  transition: (id, data) => client.post(`/applications/${id}/transition/`, data),
};

// Interviews API
export const interviewsAPI = {
  list: (params) => client.get('/interviews/', { params }),
  create: (data) => client.post('/interviews/', data),
  complete: (id, data) => client.post(`/interviews/${id}/complete/`, data),
};

// Integrations API
export const integrationsAPI = {
  list: () => client.get('/integrations/'),
  get: (id) => client.get(`/integrations/${id}/`),
  create: (data) => client.post('/integrations/', data),
  update: (id, data) => client.patch(`/integrations/${id}/`, data),
  delete: (id) => client.delete(`/integrations/${id}/`),
  testConnection: (id) => client.post(`/integrations/${id}/test_connection/`),
  triggerSync: (id, data) => client.post(`/integrations/${id}/trigger_sync/`, data),
  syncLogs: (id) => client.get(`/integrations/${id}/sync_logs/`),
};

// AI Engine API
export const aiAPI = {
  parseResume: (formData) =>
    client.post('/ai/parse-resume/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  scoreCandidate: (data) => client.post('/ai/score-candidate/', data),
  rankCandidates: (jobId) => client.post(`/ai/rank-candidates/${jobId}/`),
  generateJobDescription: (data) => client.post('/ai/generate-job-description/', data),
  generateInterviewQuestions: (data) => client.post('/ai/generate-interview-questions/', data),
  screenResume: (data) => client.post('/ai/screen-resume/', data),
};

// Analytics API
export const analyticsAPI = {
  dashboard: () => client.get('/analytics/dashboard/'),
  funnel: (params) => client.get('/analytics/funnel/', { params }),
  sources: () => client.get('/analytics/sources/'),
  trends: () => client.get('/analytics/trends/'),
  jobPerformance: () => client.get('/analytics/job-performance/'),
};

export default client;
