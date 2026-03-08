import { useState } from 'react'
import { SiMysql, SiPostgresql } from 'react-icons/si'

export default function DatabaseSelector({ value, onChange }) {
  const [showComingSoon, setShowComingSoon] = useState(false)

  const handlePostgreClick = () => {
    setShowComingSoon(true)
    setTimeout(() => setShowComingSoon(false), 3000)
  }

  return (
    <div style={{ position: 'relative' }}>
      <div className="db-selector">
        <button
          className={`db-option ${value === 'mysql' ? 'active' : ''}`}
          onClick={() => onChange('mysql')}
        >
          <SiMysql style={{ fontSize: '1.1rem' }} />
          MySQL
        </button>
        <button
          className="db-option"
          onClick={handlePostgreClick}
          style={{ opacity: 0.5, cursor: 'not-allowed' }}
        >
          <SiPostgresql style={{ fontSize: '1.1rem' }} />
          PostgreSQL
        </button>
      </div>

      {/* Coming Soon Popup */}
      {showComingSoon && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 10px)',
          left: 0,
          right: 0,
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.15))',
          border: '1px solid rgba(139, 92, 246, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '14px 18px',
          backdropFilter: 'blur(20px)',
          zIndex: 100,
          animation: 'comingSoonPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
          boxShadow: '0 8px 32px rgba(139, 92, 246, 0.2)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{
              fontSize: '1.5rem',
              animation: 'comingSoonBounce 0.6s ease infinite alternate',
            }}>🚀</span>
            <div>
              <div style={{
                fontWeight: 700,
                fontSize: '0.9rem',
                background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                PostgreSQL Analyzer — Coming Soon!
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                We're cooking something awesome 🔥
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes comingSoonPop {
          from { opacity: 0; transform: scale(0.9) translateY(8px); }
          to { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes comingSoonBounce {
          from { transform: translateY(0); }
          to { transform: translateY(-3px); }
        }
      `}</style>
    </div>
  )
}
