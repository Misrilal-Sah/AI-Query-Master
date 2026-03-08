import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { HiOutlineClock, HiOutlineTrash, HiOutlineEye, HiOutlineCode, HiOutlineDatabase, HiOutlineChatAlt2, HiOutlineServer, HiOutlineInformationCircle } from 'react-icons/hi'
import { useAuth } from '../context/AuthContext'
import api from '../api'

const featureIcons = {
  query_review: HiOutlineCode,
  schema_review: HiOutlineDatabase,
  nl_to_query: HiOutlineChatAlt2,
  live_analysis: HiOutlineServer,
}

const featureLabels = {
  query_review: 'Query Review',
  schema_review: 'Schema Review',
  nl_to_query: 'NL to Query',
  live_analysis: 'Live Analysis',
}

export default function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filter) params.append('feature', filter)
      const token = localStorage.getItem('aqm_token')
      const response = await api.get(`/history?${params.toString()}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      setItems(response.data.items || [])
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchHistory()
    } else {
      setLoading(false)
    }
  }, [filter, isAuthenticated])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this analysis?')) return
    try {
      await api.delete(`/history/${id}`)
      setItems(items.filter(item => item.id !== id))
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  // Not logged in — prompt
  if (!isAuthenticated) {
    return (
      <div className="animate-fade-in">
        <div className="page-header">
          <h1 className="page-title">
            <HiOutlineClock className="icon" />
            Analysis History
          </h1>
        </div>
        <div className="glass-card" style={{ textAlign: 'center', padding: 60 }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>🔒</div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-heading)', marginBottom: 8 }}>
            Sign In to View History
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 24, maxWidth: 400, margin: '0 auto 24px' }}>
            Your analysis history is saved automatically when you're logged in. Sign in or create an account to access your past analyses.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <Link to="/login" className="btn btn-primary btn-lg">Sign In</Link>
            <Link to="/signup" className="btn btn-secondary btn-lg">Create Account</Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <HiOutlineClock className="icon" />
          Analysis History
        </h1>
        <p className="page-subtitle">View your past query analyses and results</p>
      </div>

      {/* Filters */}
      <div className="glass-card" style={{ marginBottom: 16, padding: '12px 16px', position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <button className={`btn btn-sm ${!filter ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setFilter('')}>All</button>
          {Object.entries(featureLabels).map(([key, label]) => (
            <button
              key={key}
              className={`btn btn-sm ${filter === key ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilter(key)}
            >
              {label}
            </button>
          ))}
          <div style={{ position: 'relative', marginLeft: 'auto' }} className="schema-info-wrapper">
            <HiOutlineInformationCircle
              style={{ fontSize: '1.1rem', color: 'var(--text-muted)', cursor: 'help' }}
            />
            <div className="schema-info-tooltip">
              Schema Builder & Diagram to DDL results are not saved in history as they are one-time transformations.
            </div>
          </div>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="spinner-container"><div className="spinner" /><div className="spinner-text">Loading history...</div></div>
      ) : items.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: '2rem', marginBottom: 8 }}>📭</div>
          <div style={{ color: 'var(--text-secondary)' }}>No analyses yet</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Start analyzing queries to build your history</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {items.map((item) => {
            const Icon = featureIcons[item.feature] || HiOutlineCode
            return (
              <div
                key={item.id}
                className="glass-card history-item"
                style={{ padding: '14px 18px', cursor: 'pointer', transition: 'all 0.2s' }}
                onClick={() => navigate(`/history/${item.id}`)}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
                  <Icon style={{ fontSize: '1.2rem', color: 'var(--accent-blue)', flexShrink: 0, marginTop: 2 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginBottom: 4 }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-heading)' }}>
                        {featureLabels[item.feature] || item.feature}
                      </span>
                      <span className="issue-tag issue-info">{item.db_type}</span>
                      {item.scores?.grade && (
                        <span className={`issue-tag ${item.scores.grade <= 'B' ? 'issue-info' : 'issue-warning'}`}>
                          Grade {item.scores.grade}
                        </span>
                      )}
                    </div>
                    <div style={{
                      fontSize: '0.78rem', color: 'var(--text-muted)',
                      overflow: 'hidden', textOverflow: 'ellipsis',
                      fontFamily: 'var(--font-mono)',
                      maxWidth: '100%',
                    }} className="history-query-text">
                      {item.input_text?.substring(0, 80)}...
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', flexShrink: 0, marginLeft: 'auto' }}>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    <button className="btn btn-secondary btn-sm" onClick={(e) => { e.stopPropagation(); navigate(`/history/${item.id}`); }}>
                      <HiOutlineEye /> Open
                    </button>
                    <button
                      className="btn btn-ghost btn-icon btn-sm"
                      onClick={(e) => handleDelete(item.id, e)}
                      title="Delete"
                    >
                      <HiOutlineTrash />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <style>{`
        .history-item:hover {
          border-color: var(--border-hover) !important;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .schema-info-tooltip {
          display: none;
          position: absolute;
          right: 0;
          top: calc(100% + 8px);
          background: #0c1222;
          border: 1px solid var(--border-color);
          border-radius: var(--radius-sm);
          padding: 10px 14px;
          font-size: 0.75rem;
          color: var(--text-secondary);
          max-width: min(320px, 90vw);
          white-space: normal;
          word-wrap: break-word;
          z-index: 100;
          box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        [data-theme="light"] .schema-info-tooltip {
          background: #ffffff;
          box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        .schema-info-wrapper:hover .schema-info-tooltip {
          display: block;
        }
        .history-query-text {
          white-space: nowrap;
        }
        @media (max-width: 600px) {
          .history-item > div {
            flex-direction: column !important;
          }
          .history-item > div > div:last-child {
            width: 100%;
            margin-top: 8px;
            justify-content: flex-start;
          }
          .history-query-text {
            white-space: normal !important;
            word-break: break-all;
          }
        }
      `}</style>
    </div>
  )
}
