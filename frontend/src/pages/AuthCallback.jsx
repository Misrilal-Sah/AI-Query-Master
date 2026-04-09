import { useEffect, useState, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../api'

function decodeJwtPayload(token) {
  const parts = token.split('.')
  if (parts.length < 2) {
    throw new Error('Invalid token format')
  }

  const base64Url = parts[1]
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
  const padding = '='.repeat((4 - (base64.length % 4)) % 4)
  return JSON.parse(atob(base64 + padding))
}

export default function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('loading')
  const [errorMsg, setErrorMsg] = useState('')
  const exchangedRef = useRef(false) // Prevent double exchange in StrictMode

  useEffect(() => {
    if (exchangedRef.current) return
    exchangedRef.current = true
    handleCallback()
  }, [])

  const handleCallback = async () => {
    // 1. Check for error in query params
    const error = searchParams.get('error')
    const errorDesc = searchParams.get('error_description')

    if (error) {
      setStatus('error')
      setErrorMsg(errorDesc?.replace(/\+/g, ' ') || error)
      return
    }

    // 2. Check for PKCE code (?code=...)
    const code = searchParams.get('code')
    if (code) {
      try {
        const response = await api.post('/auth/exchange-code', { code })
        const { user, access_token } = response.data

        localStorage.setItem('aqm_user', JSON.stringify(user))
        localStorage.setItem('aqm_token', access_token)

        setStatus('success')
        setTimeout(() => {
          navigate('/', { replace: true })
          window.location.reload()
        }, 1500)
        return
      } catch (e) {
        setStatus('error')
        setErrorMsg(e?.message || 'Failed to complete sign in.')
        return
      }
    }

    // 3. Check for hash fragment tokens (#access_token=...)
    const hash = window.location.hash.substring(1)
    if (hash) {
      const hashParams = new URLSearchParams(hash)
      const accessToken = hashParams.get('access_token')
      if (accessToken) {
        try {
          const payload = decodeJwtPayload(accessToken)
          const user = {
            id: payload.sub,
            email: payload.email,
            full_name: payload.user_metadata?.full_name || payload.user_metadata?.name || payload.email?.split('@')[0],
          }
          localStorage.setItem('aqm_user', JSON.stringify(user))
          localStorage.setItem('aqm_token', accessToken)
          setStatus('success')
          setTimeout(() => {
            navigate('/', { replace: true })
            window.location.reload()
          }, 1500)
          return
        } catch {
          setStatus('error')
          setErrorMsg('Failed to process authentication token')
          return
        }
      }
    }

    setStatus('error')
    setErrorMsg('No authentication token received. Please try again.')
  }

  return (
    <div className="auth-page">
      <div className="auth-card glass-card" style={{ textAlign: 'center', padding: 48 }}>
        {status === 'loading' && (
          <div className="animate-fade-in">
            <div className="spinner" style={{ margin: '0 auto 20px', width: 48, height: 48 }} />
            <h2 style={{ color: 'var(--text-heading)', fontSize: '1.3rem', marginBottom: 8 }}>Signing you in...</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Please wait</p>
          </div>
        )}

        {status === 'success' && (
          <div className="animate-fade-in">
            <svg viewBox="0 0 52 52" style={{ width: 64, height: 64, margin: '0 auto 20px', display: 'block' }}>
              <circle cx="26" cy="26" r="25" fill="none" stroke="#10b981" strokeWidth="2"
                style={{ strokeDasharray: 157, strokeDashoffset: 0, animation: 'circleAnim 0.6s ease' }} />
              <path fill="none" stroke="#10b981" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"
                d="M14.1 27.2l7.1 7.2 16.7-16.8"
                style={{ strokeDasharray: 48, strokeDashoffset: 0, animation: 'checkAnim 0.4s 0.3s ease both' }} />
            </svg>
            <h2 style={{ color: 'var(--accent-green)', fontSize: '1.3rem', marginBottom: 8 }}>Welcome! 🎉</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Redirecting to dashboard...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="animate-fade-in">
            <div style={{ fontSize: '3.5rem', marginBottom: 16, animation: 'shakeAnim 0.5s ease' }}>❌</div>
            <h2 style={{ color: 'var(--accent-red)', fontSize: '1.3rem', marginBottom: 8 }}>Authentication Failed</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 24, maxWidth: 350, margin: '0 auto 24px' }}>{errorMsg}</p>
            <button className="btn btn-primary" onClick={() => navigate('/login')}>Back to Login</button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes circleAnim { from { stroke-dashoffset: 157; } to { stroke-dashoffset: 0; } }
        @keyframes checkAnim { from { stroke-dashoffset: 48; } to { stroke-dashoffset: 0; } }
        @keyframes shakeAnim { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-8px)} 40%{transform:translateX(8px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(4px)} }
      `}</style>
    </div>
  )
}
