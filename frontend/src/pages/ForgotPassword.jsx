import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { HiOutlineMail, HiOutlineRefresh } from 'react-icons/hi'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)
  const { forgotPassword } = useAuth()

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendCooldown])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await forgotPassword(email)
      setSent(true)
      setResendCooldown(60)
    } catch (err) {
      setError(err.message || 'Failed to send reset email')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (resendCooldown > 0) return
    setLoading(true)
    setError('')
    try {
      await forgotPassword(email)
      setResendCooldown(60)
    } catch (err) {
      setError('Resend failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="auth-page">
        <div className="auth-card glass-card" style={{ textAlign: 'center', padding: 48 }}>
          <div className="animate-fade-in">
            <div style={{
              width: 72, height: 72, margin: '0 auto 20px',
              background: 'linear-gradient(135deg, #f59e0b, #ef4444)',
              borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center',
              animation: 'bounceIn 0.6s ease',
            }}>
              <HiOutlineMail style={{ fontSize: '2rem', color: 'white' }} />
            </div>

            <h2 style={{ color: 'var(--text-heading)', fontSize: '1.4rem', fontWeight: 800, marginBottom: 12 }}>
              Check Your Email
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: 4 }}>
              If an account exists for
            </p>
            <p style={{
              color: 'var(--accent-blue)', fontWeight: 700, fontSize: '1rem',
              marginBottom: 8,
            }}>
              {email}
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 28 }}>
              we've sent a password reset link.
            </p>

            {error && (
              <div className="notice notice-warning mb-4">
                <span>{error}</span>
              </div>
            )}

            {/* Resend button with timer */}
            <button
              className="btn btn-secondary"
              onClick={handleResend}
              disabled={resendCooldown > 0 || loading}
              style={{ marginBottom: 16, width: '100%', justifyContent: 'center' }}
            >
              <HiOutlineRefresh style={loading ? { animation: 'spin 1s linear infinite' } : {}} />
              {resendCooldown > 0
                ? `Resend in ${resendCooldown}s`
                : 'Resend Reset Email'
              }
            </button>

            <Link
              to="/login"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', display: 'flex' }}
            >
              Back to Login
            </Link>

            <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 16 }}>
              Didn't receive it? Check your spam folder.
            </p>
          </div>

          <style>{`
            @keyframes bounceIn {
              0% { transform: scale(0); opacity: 0; }
              50% { transform: scale(1.15); }
              100% { transform: scale(1); opacity: 1; }
            }
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card glass-card">
        <div className="auth-logo">
          <div className="logo-icon">QM</div>
          <h1 className="auth-title">Reset Password</h1>
          <p className="auth-subtitle">Enter your email and we'll send you a reset link</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group mb-4">
            <label className="form-label">Email</label>
            <input
              className="input"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {error && (
            <div className="notice notice-warning mb-4">
              <span>{error}</span>
            </div>
          )}

          <button className="btn btn-primary w-full btn-lg" type="submit" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <p className="auth-link mt-4">
          <Link to="/login">← Back to Login</Link>
        </p>
      </div>
    </div>
  )
}
