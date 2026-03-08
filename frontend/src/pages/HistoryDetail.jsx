import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { HiOutlineArrowLeft, HiOutlineCode, HiOutlineDatabase, HiOutlineChatAlt2, HiOutlineServer } from 'react-icons/hi'
import ResultPanel from '../components/ResultPanel'
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

export default function HistoryDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const token = localStorage.getItem('aqm_token')
        const response = await api.get(`/history/${id}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        setItem(response.data)
      } catch (err) {
        setError('Failed to load analysis details')
      } finally {
        setLoading(false)
      }
    }
    fetchItem()
  }, [id])

  if (loading) {
    return (
      <div className="animate-fade-in" style={{ padding: 40 }}>
        <div className="spinner-container">
          <div className="spinner" />
          <div className="spinner-text">Loading analysis...</div>
        </div>
      </div>
    )
  }

  if (error || !item) {
    return (
      <div className="animate-fade-in">
        <div className="glass-card" style={{ textAlign: 'center', padding: 48 }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>😕</div>
          <h2 style={{ color: 'var(--text-heading)', marginBottom: 8 }}>Analysis Not Found</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>{error}</p>
          <button className="btn btn-primary" onClick={() => navigate('/history')}>Back to History</button>
        </div>
      </div>
    )
  }

  const Icon = featureIcons[item.feature] || HiOutlineCode
  const label = featureLabels[item.feature] || item.feature

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button className="btn btn-ghost btn-icon" onClick={() => navigate('/history')} title="Back to History">
          <HiOutlineArrowLeft />
        </button>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Icon style={{ fontSize: '1.3rem', color: 'var(--accent-blue)' }} />
            <h1 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-heading)', margin: 0 }}>
              {label}
            </h1>
            <span className="issue-tag issue-info">{item.db_type}</span>
            {item.scores?.grade && (
              <span className={`issue-tag ${item.scores.grade <= 'B' ? 'issue-info' : 'issue-warning'}`}>
                Grade {item.scores.grade}
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>
            {new Date(item.created_at).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="glass-card" style={{ marginBottom: 16 }}>
        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-heading)', marginBottom: 10 }}>
          Input Query
        </h3>
        <pre style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.85rem',
          lineHeight: 1.7,
          whiteSpace: 'pre-wrap',
          color: 'var(--text-secondary)',
          background: 'var(--bg-nested)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)',
          padding: 16,
          maxHeight: 200,
          overflow: 'auto',
        }}>
          {item.input_text}
        </pre>
      </div>

      {/* Full Result Panel — same as the original feature page */}
      <ResultPanel result={item.result || item} loading={false} />
    </div>
  )
}
