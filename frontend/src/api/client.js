/**
 * LoanPilot — API Client
 * =======================
 * Axios instance with base URL configuration and error interceptor.
 *
 * Usage: import api from '../api/client'
 *        api.get('/applications')
 */

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    console.error(`API Error: ${message}`);
    return Promise.reject(error);
  }
);

export default api;
