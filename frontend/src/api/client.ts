import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('civilcortex_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle unauthenticated sessions and standardize errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Check if it's an unauthenticated error
    if (error.response?.status === 401) {
      localStorage.removeItem('civilcortex_token');
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    // Standardize error message extraction from our new error taxonomy
    let errorMessage = 'An unexpected error occurred';
    let errorCode = 'UNKNOWN_ERROR';
    
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error.message || errorMessage;
      errorCode = error.response.data.error.code || errorCode;
    } else if (error.response?.data?.detail) {
      // Fallback for FastAPI default HTTPExceptions
      if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail;
      } else if (Array.isArray(error.response.data.detail)) {
        errorMessage = error.response.data.detail[0]?.msg || errorMessage;
        errorCode = 'VALIDATION_ERROR';
      }
    } else if (error.message) {
      errorMessage = error.message;
    }

    // Enhance the error object so consumers can easily access it
    error.civilCortexMessage = errorMessage;
    error.civilCortexCode = errorCode;

    return Promise.reject(error);
  }
);
