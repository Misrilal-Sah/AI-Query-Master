import axios from 'axios'

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
const normalizedApiBaseUrl = rawApiBaseUrl ? rawApiBaseUrl.replace(/\/+$/, '') : ''
const currentHostname = typeof window !== 'undefined' ? window.location.hostname : ''
const knownFrontendHosts = new Set(['ai-query-master.misril.dev', 'www.ai-query-master.misril.dev'])
const inferredProdApiBaseUrl = knownFrontendHosts.has(currentHostname)
  ? 'https://ai-query-master.onrender.com/api'
  : '/api'
const defaultApiBaseUrl = import.meta.env.DEV ? 'http://localhost:8000/api' : inferredProdApiBaseUrl

export const API_BASE_URL = normalizedApiBaseUrl || defaultApiBaseUrl
export const GOOGLE_AUTH_URL = `${API_BASE_URL.replace(/\/api\/?$/, '')}/api/auth/google`

const api = axios.create({
  baseURL: API_BASE_URL,
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
