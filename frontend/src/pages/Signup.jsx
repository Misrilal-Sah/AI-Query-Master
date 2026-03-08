import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FcGoogle } from 'react-icons/fc'
import { HiOutlineMail, HiOutlineRefresh } from 'react-icons/hi'

export default function Signup() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)
  const { signup, loginWithGoogle } = useAuth()

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendCooldown])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)
    setError('')

    try {
      await signup(email, password, fullName)
      setSuccess(true)
      setResendCooldown(60)
    } catch (err) {
      setError(err.message || 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (resendCooldown > 0) return
    setLoading(true)
    try {
      await signup(email, password, fullName)
      setResendCooldown(60)
    } catch (err) {
      setError('Resend failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card glass-card" style={{ textAlign: 'center', padding: 48 }}>
          <div className="animate-fade-in">
            {/* Animated envelope */}
            <div style={{
              width: 72, height: 72, margin: '0 auto 20px',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center',
              animation: 'bounceIn 0.6s ease',
            }}>
              <HiOutlineMail style={{ fontSize: '2rem', color: 'white' }} />
            </div>

            <h2 style={{ color: 'var(--text-heading)', fontSize: '1.4rem', fontWeight: 800, marginBottom: 12 }}>
              Check Your Email
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: 4 }}>
              We've sent a confirmation link to
            </p>
            <p style={{
              color: 'var(--accent-blue)', fontWeight: 700, fontSize: '1rem',
              marginBottom: 8,
            }}>
              {email}
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 28 }}>
              Please click the link to activate your account.
            </p>

            {/* Resend button */}
            <button
              className="btn btn-secondary"
              onClick={handleResend}
              disabled={resendCooldown > 0 || loading}
              style={{ marginBottom: 16, width: '100%', justifyContent: 'center' }}
            >
              <HiOutlineRefresh style={loading ? { animation: 'spin 1s linear infinite' } : {}} />
              {resendCooldown > 0
                ? `Resend in ${resendCooldown}s`
                : 'Resend Confirmation Email'
              }
            </button>

            <Link
              to="/login"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', display: 'flex' }}
            >
              Go to Login
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
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Sign up to save and access your analysis history</p>
        </div>

        {/* Google Auth */}
        <button className="google-btn" onClick={loginWithGoogle} type="button">
          <FcGoogle style={{ fontSize: '1.2rem' }} />
          Continue with Google
        </button>

        <div className="auth-divider">or</div>

        <form onSubmit={handleSubmit}>
          <div className="form-group mb-4">
            <label className="form-label">Full Name</label>
            <input
              className="input"
              type="text"
              placeholder="Your name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

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

          <div className="form-group mb-4">
            <label className="form-label">Password</label>
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

          {error && (
            <div className="notice notice-warning mb-4" style={{ animation: 'shakeAnim 0.4s ease' }}>
              <span>{error}</span>
            </div>
          )}

          <button className="btn btn-primary w-full btn-lg" type="submit" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-link mt-4">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
        <p className="auth-link mt-2">
          <Link to="/" style={{ color: 'var(--text-muted)' }}>← Continue without signing in</Link>
        </p>

        <style>{`
          @keyframes shakeAnim { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)} }
        `}</style>
      </div>
    </div>
  )
}
