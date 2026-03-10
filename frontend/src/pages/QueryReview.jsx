import { useState } from 'react'
import { HiOutlineCode, HiOutlinePlay } from 'react-icons/hi'
import DatabaseSelector from '../components/DatabaseSelector'
import ResultPanel from '../components/ResultPanel'
import api from '../api'

export default function QueryReview() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await api.post('/review-query', {
        query: query.trim(),
        db_type: 'mysql',
      })
      setResult(response.data)
    } catch (err) {
      setError(err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExampleQuery = () => {
    setQuery(`SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE status = 'pending') ORDER BY created_at;`)
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <HiOutlineCode className="icon" />
          Query Review & Optimization
        </h1>
        <p className="page-subtitle">
          Analyze SQL queries for performance, security, and readability issues
        </p>
      </div>

      <div className="flex-col gap-4" style={{ display: 'flex' }}>
        {/* Input Section */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-4" style={{ display: 'flex' }}>
            <div className="form-label">Database Type</div>
            <button className="btn btn-ghost btn-sm" onClick={handleExampleQuery}>
              Load Example
            </button>
          </div>
          <DatabaseSelector />

          <div className="form-group mt-4">
            <label className="form-label">SQL Query</label>
            <textarea
              className="textarea textarea-lg"
              placeholder={`Enter your MySQL query here...\n\nExample:\nSELECT * FROM users WHERE id IN (SELECT user_id FROM orders);`}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <div className="mt-4" style={{ display: 'flex', gap: 12 }}>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleSubmit}
              disabled={loading || !query.trim()}
            >
              <HiOutlinePlay />
              {loading ? 'Analyzing...' : 'Analyze Query'}
            </button>
            {query && (
              <button className="btn btn-ghost" onClick={() => { setQuery(''); setResult(null); setError(''); }}>
                Clear
              </button>
            )}
          </div>

          {error && (
            <div className="notice notice-warning mt-4">
              <span className="notice-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Results */}
        <ResultPanel result={result} loading={loading} />
      </div>
    </div>
  )
}
