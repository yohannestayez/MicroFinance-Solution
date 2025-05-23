import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  // Use relative URL to leverage Vite's proxy or environment variable for production
  baseURL: '/api/v1', // This will be proxied by Vite in development
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // Disable for now to avoid CORS preflight issues
});

// Add a request interceptor to handle authentication
api.interceptors.request.use(
  (config) => {
    // Get the session ID from storage
    const sessionId = localStorage.getItem('session_id');
    
    // If we have a session ID, add it to the Authorization header
    if (sessionId) {
      config.headers['Authorization'] = `Bearer ${sessionId}`;
    }
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    // Log successful responses in development
    if (import.meta.env.DEV) {
      console.log(`API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    const { response } = error;
    
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error('API Error:', error.message, response?.status, response?.data);
    }
    
    // Handle authentication errors
    if (response && response.status === 401) {
      // Clear user and session from sessionStorage
      // Clear user and session from sessionStorage
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('session_id');
      sessionStorage.removeItem('session_id');
      
      // Only redirect if we're not already on the login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login?session=expired';
      }
    }
    
    // Handle server errors
    if (response && response.status >= 500) {
      console.error('Server error:', response.status, response.data);
    }
    
    return Promise.reject(error);
  }
);

export default api;
