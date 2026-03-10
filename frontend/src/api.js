import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
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
