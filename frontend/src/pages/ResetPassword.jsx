import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { HiOutlineLockClosed, HiOutlineCheck } from 'react-icons/hi'

export default function ResetPassword() {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [accessToken, setAccessToken] = useState(null)
  const { updatePassword } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    // Extract access_token from URL hash (Supabase recovery redirect)
    const hash = window.location.hash
    const params = new URLSearchParams(hash.replace('#', ''))
    const token = params.get('access_token')
    if (token) {
      setAccessToken(token)
      // Clean hash from URL
      window.history.replaceState(null, '', window.location.pathname)
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    setError('')

    try {
      await updatePassword(accessToken, password)
      setSuccess(true)
    } catch (err) {
      setError(err.message || 'Failed to update password')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card glass-card" style={{ textAlign: 'center', padding: 48 }}>
          <div className="animate-fade-in">
            <div style={{
              width: 72, height: 72, margin: '0 auto 20px',
              background: 'linear-gradient(135deg, #10b981, #06b6d4)',
              borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center',
              animation: 'bounceIn 0.6s ease',
            }}>
              <HiOutlineCheck style={{ fontSize: '2rem', color: 'white' }} />
            </div>

            <h2 style={{ color: 'var(--text-heading)', fontSize: '1.4rem', fontWeight: 800, marginBottom: 12 }}>
              Password Updated!
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: 24 }}>
              Your password has been successfully changed. You can now sign in with your new password.
            </p>

            <Link
              to="/login"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', display: 'flex' }}
            >
              Go to Login
            </Link>
          </div>

          <style>{`
            @keyframes bounceIn {
              0% { transform: scale(0); opacity: 0; }
              50% { transform: scale(1.15); }
              100% { transform: scale(1); opacity: 1; }
            }
          `}</style>
        </div>
      </div>
    )
  }

  if (!accessToken) {
    return (
      <div className="auth-page">
        <div className="auth-card glass-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</div>
          <h2 className="auth-title">Invalid Reset Link</h2>
          <p className="auth-subtitle">
            This password reset link is invalid or has expired. Please request a new one.
          </p>
          <Link to="/forgot-password" className="btn btn-primary mt-4" style={{ display: 'inline-flex' }}>
            Request New Link
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card glass-card">
        <div className="auth-logo">
          <div style={{
            width: 48, height: 48,
            background: 'linear-gradient(135deg, #f59e0b, #ef4444)',
            borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 12px',
          }}>
            <HiOutlineLockClosed style={{ fontSize: '1.5rem', color: 'white' }} />
          </div>
          <h1 className="auth-title">Set New Password</h1>
          <p className="auth-subtitle">Enter your new password below</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group mb-4">
            <label className="form-label">New Password</label>
            <input
              className="input"
              type="password"
              placeholder="Min. 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <div className="form-group mb-4">
            <label className="form-label">Confirm Password</label>
            <input
              className="input"
              type="password"
              placeholder="Repeat your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {error && (
            <div className="notice notice-warning mb-4" style={{ animation: 'shakeAnim 0.4s ease' }}>
              <span>{error}</span>
            </div>
          )}

          <button className="btn btn-primary w-full btn-lg" type="submit" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? 'Updating...' : 'Update Password'}
          </button>
        </form>

        <p className="auth-link mt-4">
          <Link to="/login">← Back to Login</Link>
        </p>

        <style>{`
          @keyframes shakeAnim { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)} }
        `}</style>
      </div>
    </div>
  )
}
