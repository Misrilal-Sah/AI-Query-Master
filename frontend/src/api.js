import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 300000, // 5 minutes for large DB analysis
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    console.error('API Error:', message)
    return Promise.reject({ message, status: error.response?.status })
  }
)

export default api
