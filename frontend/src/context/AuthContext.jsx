import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem('aqm_user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch {}
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    const userData = response.data.user
    setUser(userData)
    localStorage.setItem('aqm_user', JSON.stringify(userData))
    localStorage.setItem('aqm_token', response.data.access_token)
    return response.data
  }

  const signup = async (email, password, fullName) => {
    const response = await api.post('/auth/signup', { email, password, full_name: fullName })
    return response.data
  }

  const loginWithGoogle = () => {
    // Redirect to backend Google OAuth endpoint
    window.location.href = 'http://localhost:8000/api/auth/google'
  }

  const forgotPassword = async (email) => {
    const response = await api.post('/auth/forgot-password', { email })
    return response.data
  }

  const updatePassword = async (accessToken, newPassword) => {
    const response = await api.post('/auth/update-password', {
      access_token: accessToken,
      new_password: newPassword,
    })
    return response.data
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('aqm_user')
    localStorage.removeItem('aqm_token')
  }

  return (
    <AuthContext.Provider value={{
      user, loading, login, signup, loginWithGoogle, forgotPassword, updatePassword, logout, isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
