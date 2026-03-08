import { useState } from 'react'
import { HiOutlineDatabase, HiOutlinePlay } from 'react-icons/hi'
import DatabaseSelector from '../components/DatabaseSelector'
import ResultPanel from '../components/ResultPanel'
import api from '../api'

export default function SchemaReview() {
  const [schema, setSchema] = useState('')
  const [dbType, setDbType] = useState('mysql')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!schema.trim()) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await api.post('/review-schema', {
        schema: schema.trim(),
        db_type: dbType,
      })
      setResult(response.data)
    } catch (err) {
      setError(err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExample = () => {
    const examples = {
      mysql: `CREATE TABLE users (
  id INT,
  name TEXT,
  email TEXT,
  password TEXT,
  status TEXT
);

CREATE TABLE orders (
  id INT,
  user_id INT,
  amount FLOAT,
  product TEXT,
  date TEXT
);`,
      postgresql: `CREATE TABLE users (
  id INTEGER,
  name TEXT,
  email TEXT,
  password TEXT,
  status TEXT
);

CREATE TABLE orders (
  id INTEGER,
  user_id INTEGER,
  amount NUMERIC,
  product TEXT,
  created_date TEXT
);`,
    }
    setSchema(examples[dbType])
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <HiOutlineDatabase className="icon" />
          Schema Review
        </h1>
        <p className="page-subtitle">
          Evaluate database schema design and get improvement suggestions
        </p>
      </div>

      <div className="flex-col gap-4" style={{ display: 'flex' }}>
        <div className="glass-card">
          <div className="flex items-center justify-between mb-4" style={{ display: 'flex' }}>
            <div className="form-label">Database Type</div>
            <button className="btn btn-ghost btn-sm" onClick={handleExample}>
              Load Example
            </button>
          </div>
          <DatabaseSelector value={dbType} onChange={setDbType} />

          <div className="form-group mt-4">
            <label className="form-label">Schema DDL</label>
            <textarea
              className="textarea textarea-lg"
              placeholder={`Enter your CREATE TABLE statements...\n\nExample:\nCREATE TABLE users (\n  id INT,\n  name TEXT,\n  email TEXT\n);`}
              value={schema}
              onChange={(e) => setSchema(e.target.value)}
              style={{ minHeight: 240 }}
            />
          </div>

          <div className="mt-4" style={{ display: 'flex', gap: 12 }}>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleSubmit}
              disabled={loading || !schema.trim()}
            >
              <HiOutlinePlay />
              {loading ? 'Analyzing...' : 'Review Schema'}
            </button>
            {schema && (
              <button className="btn btn-ghost" onClick={() => { setSchema(''); setResult(null); setError(''); }}>
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

        <ResultPanel result={result} loading={loading} />
      </div>
    </div>
  )
}
