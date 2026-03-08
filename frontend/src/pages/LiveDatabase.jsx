import { useState } from 'react'
import {
  HiOutlineServer, HiOutlinePlay, HiOutlineX,
  HiOutlineExclamation, HiOutlineShieldCheck,
  HiOutlineMicrophone, HiOutlineStop,
  HiOutlineInformationCircle,
} from 'react-icons/hi'
import DatabaseSelector from '../components/DatabaseSelector'
import ResultPanel from '../components/ResultPanel'
import api from '../api'

export default function LiveDatabase() {
  const [dbType, setDbType] = useState('mysql')
  const [credentials, setCredentials] = useState({
    host: '',
    port: 3306,
    database: '',
    username: '',
    password: '',
  })
  const [sessionId, setSessionId] = useState(null)
  const [schemaData, setSchemaData] = useState(null)
  const [query, setQuery] = useState('')
  const [inputMode, setInputMode] = useState('sql') // 'sql' or 'nl'
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [error, setError] = useState('')
  const [listening, setListening] = useState(false)
  const [showInfo, setShowInfo] = useState(false)
  const [showSchema, setShowSchema] = useState(false)

  const updateField = (field, value) => {
    setCredentials(prev => ({ ...prev, [field]: value }))
  }

  const handleDbTypeChange = (type) => {
    setDbType(type)
    setCredentials(prev => ({
      ...prev,
      port: type === 'mysql' ? 3306 : 5432,
    }))
  }

  const handleConnect = async () => {
    setConnecting(true)
    setError('')

    try {
      const response = await api.post('/connect-db', {
        ...credentials,
        port: parseInt(credentials.port),
        db_type: dbType,
      })

      setSessionId(response.data.session_id)

      const schemaResponse = await api.post('/db-schema', {
        session_id: response.data.session_id,
      })
      setSchemaData(schemaResponse.data)
    } catch (err) {
      setError(err.message || 'Connection failed')
    } finally {
      setConnecting(false)
    }
  }

  const handleDisconnect = async () => {
    try {
      await api.post('/disconnect-db', { session_id: sessionId })
    } catch (err) {}
    setSessionId(null)
    setSchemaData(null)
    setResult(null)
    setQuery('')
  }

  const handleAnalyze = async () => {
    if (!sessionId) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      // If NL mode, first convert to SQL, then analyze
      if (inputMode === 'nl' && query.trim()) {
        // Build rich schema context from connected DB
        let schemaContext = ''
        if (schemaData?.tables) {
          schemaContext = schemaData.tables.map(t => {
            const cols = t.columns?.map(c =>
              `${c.COLUMN_NAME || c.column_name} ${c.DATA_TYPE || c.data_type}${c.COLUMN_KEY === 'PRI' ? ' PK' : ''}`
            ).join(', ') || ''
            return `${t.name}(${cols})`
          }).join('\n')
        }
        const nlResponse = await api.post('/nl-to-query', {
          description: query.trim(),
          db_type: dbType,
          schema_context: schemaContext,
        })
        setResult(nlResponse.data)
      } else {
        const response = await api.post('/analyze-live', {
          session_id: sessionId,
          query: query.trim() || undefined,
        })
        setResult(response.data)
      }
    } catch (err) {
      setError(err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExplain = async () => {
    if (!sessionId || !query.trim() || inputMode === 'nl') return
    setLoading(true)
    setError('')

    try {
      const response = await api.post('/explain', {
        session_id: sessionId,
        query: query.trim(),
      })
      setResult(prev => ({
        ...prev,
        explain_result: response.data,
      }))
    } catch (err) {
      setError(err.message || 'EXPLAIN failed')
    } finally {
      setLoading(false)
    }
  }

  // Speech-to-text
  const toggleSpeech = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      setError('Speech recognition not supported in this browser')
      return
    }

    if (listening) {
      window._speechRecognition?.stop()
      setListening(false)
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let transcript = Array.from(event.results)
        .map(r => r[0].transcript)
        .join('')

      // In SQL mode, convert common speech patterns to SQL syntax
      if (inputMode === 'sql') {
        transcript = transcript
          .replace(/\bselect\s+star\b/gi, 'SELECT *')
          .replace(/\bstar\b/gi, '*')
          .replace(/\bequals\b/gi, '=')
          .replace(/\bnot equals\b/gi, '!=')
          .replace(/\bgreater than or equal\b/gi, '>=')
          .replace(/\bless than or equal\b/gi, '<=')
          .replace(/\bgreater than\b/gi, '>')
          .replace(/\bless than\b/gi, '<')
          .replace(/\bsemicolon\b/gi, ';')
          .replace(/\bopen parenthesis\b/gi, '(')
          .replace(/\bclose parenthesis\b/gi, ')')
      }
      setQuery(transcript)
    }

    recognition.onend = () => setListening(false)
    recognition.onerror = () => setListening(false)

    window._speechRecognition = recognition
    recognition.start()
    setListening(true)
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <HiOutlineServer className="icon" />
          Live Database Analysis
        </h1>
        <p className="page-subtitle">
          Connect to a database to analyze real schemas and query performance
        </p>
      </div>

      <div className="flex-col gap-4" style={{ display: 'flex' }}>
        {/* Security Notice */}
        <div className="notice notice-warning">
          <HiOutlineShieldCheck className="notice-icon" />
          <div>
            <strong>Security Notice:</strong> Database credentials are stored{' '}
            <strong>in-memory only</strong> for the duration of your session. They are{' '}
            <strong>never persisted</strong> to disk or any database. Connection is{' '}
            <strong>read-only mode</strong>.
          </div>
        </div>

        {!sessionId ? (
          /* Connection Form */
          <div className="glass-card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 16, color: 'var(--text-heading)' }}>
              Connect to Database
            </h3>

            <div className="mb-4">
              <div className="form-label" style={{ marginBottom: 8 }}>Database Type</div>
              <DatabaseSelector value={dbType} onChange={handleDbTypeChange} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Host</label>
                <input className="input" placeholder="localhost" value={credentials.host}
                  onChange={(e) => updateField('host', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Port</label>
                <input className="input" type="number" placeholder={dbType === 'mysql' ? '3306' : '5432'}
                  value={credentials.port} onChange={(e) => updateField('port', e.target.value)} />
              </div>
            </div>

            <div className="form-group mt-2">
              <label className="form-label">Database Name</label>
              <input className="input" placeholder="my_database" value={credentials.database}
                onChange={(e) => updateField('database', e.target.value)} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }} className="mt-2">
              <div className="form-group">
                <label className="form-label">Username</label>
                <input className="input" placeholder="root" value={credentials.username}
                  onChange={(e) => updateField('username', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input className="input" type="password" placeholder="••••••••" value={credentials.password}
                  onChange={(e) => updateField('password', e.target.value)} />
              </div>
            </div>

            <button className="btn btn-success btn-lg mt-4" onClick={handleConnect}
              disabled={connecting || !credentials.database || !credentials.username}>
              <HiOutlineServer />
              {connecting ? 'Connecting...' : 'Connect (Read-Only)'}
            </button>

            {error && (
              <div className="notice notice-warning mt-4">
                <HiOutlineExclamation className="notice-icon" />
                <span>{error}</span>
              </div>
            )}
          </div>
        ) : (
          /* Connected State */
          <>
            <div className="glass-card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                <div className="notice notice-success" style={{ marginBottom: 0, padding: '8px 14px' }}>
                  <span>✓ Connected to <strong>{credentials.database}</strong> ({dbType}) — Read-only mode</span>
                </div>
                <button className="btn btn-danger btn-sm" onClick={handleDisconnect}>
                  <HiOutlineX /> Disconnect
                </button>
              </div>
            </div>

            {/* Schema Explorer — Toggleable, default OFF */}
            {schemaData && schemaData.tables && (
              <div className="glass-card">
                <button
                  onClick={() => setShowSchema(!showSchema)}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                    padding: 0, color: 'var(--text-heading)',
                  }}
                >
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>
                    {showSchema ? '▾' : '▸'} Schema ({schemaData.table_count} tables)
                  </h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {showSchema ? 'Click to collapse' : 'Click to explore'}
                  </span>
                </button>
                {showSchema && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}>
                    {schemaData.tables.map((table, i) => (
                      <details key={i} style={{
                        background: 'rgba(15, 23, 42, 0.5)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '10px 14px',
                      }}>
                        <summary style={{ cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}>
                          📋 {table.name}
                          <span style={{ color: 'var(--text-muted)', fontWeight: 400, marginLeft: 8 }}>
                            ({table.columns?.length || 0} columns{table.rows ? `, ~${table.rows} rows` : ''})
                          </span>
                        </summary>
                        <div style={{ marginTop: 8, paddingLeft: 16 }}>
                          {table.columns?.map((col, j) => (
                            <div key={j} style={{
                              fontSize: '0.8rem', color: 'var(--text-secondary)',
                              padding: '2px 0', fontFamily: 'var(--font-mono)',
                            }}>
                              {col.COLUMN_NAME || col.column_name}{' '}
                              <span style={{ color: 'var(--accent-cyan)' }}>
                                {col.DATA_TYPE || col.data_type}
                              </span>
                              {(col.COLUMN_KEY === 'PRI' || col.column_default?.includes('nextval')) && (
                                <span style={{ color: 'var(--accent-orange)', marginLeft: 6 }}>PK</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Input Mode Toggle + Query Input */}
            <div className="glass-card">
              {/* Mode Toggle */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
                <div className="db-selector" style={{ flex: 'none' }}>
                  <button
                    className={`db-option ${inputMode === 'sql' ? 'active' : ''}`}
                    onClick={() => setInputMode('sql')}
                  >
                    💻 SQL Query
                  </button>
                  <button
                    className={`db-option ${inputMode === 'nl' ? 'active' : ''}`}
                    onClick={() => setInputMode('nl')}
                  >
                    💬 Natural Language
                  </button>
                </div>
                {inputMode === 'nl' && (
                  <button
                    className={`mic-btn ${listening ? 'listening' : ''}`}
                    onClick={toggleSpeech}
                    title={listening ? 'Stop listening' : 'Speak your query'}
                  >
                    {listening ? <HiOutlineStop /> : <HiOutlineMicrophone />}
                  </button>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">
                  {inputMode === 'sql'
                    ? 'SQL Query (for EXPLAIN & analysis)'
                    : 'Describe what you want in plain English'
                  }
                </label>
                <textarea
                  className="textarea"
                  placeholder={
                    inputMode === 'sql'
                      ? 'Enter a SELECT query to analyze with EXPLAIN...'
                      : 'e.g. "Give me all movies released in the last 2 weeks"'
                  }
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>

              <div className="mt-4" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <button className="btn btn-primary btn-lg" onClick={handleAnalyze} disabled={loading}>
                  <HiOutlinePlay />
                  {loading ? 'Analyzing...' : inputMode === 'nl' ? 'Generate & Analyze' : 'Run AI Analysis'}
                </button>
                {inputMode === 'sql' && query.trim() && (
                  <button className="btn btn-secondary" onClick={handleExplain} disabled={loading}>
                    Run EXPLAIN
                  </button>
                )}
                <button
                  className="btn btn-ghost btn-icon"
                  onClick={() => setShowInfo(!showInfo)}
                  title="What do these buttons do?"
                  style={{ fontSize: '1.2rem', color: showInfo ? 'var(--accent-blue)' : 'var(--text-muted)' }}
                >
                  <HiOutlineInformationCircle />
                </button>
              </div>

              {showInfo && (
                <div className="notice notice-info mt-4" style={{ flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <span style={{ fontWeight: 700, whiteSpace: 'nowrap' }}>🔬 Run AI Analysis</span>
                    <span style={{ fontSize: '0.82rem' }}>
                      Sends your schema + query through a full AI pipeline: static analysis → RAG knowledge retrieval → LLM reasoning → self-reflection → scoring. Gives you issues, optimized query, and performance tips.
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <span style={{ fontWeight: 700, whiteSpace: 'nowrap' }}>⚡ Run EXPLAIN</span>
                    <span style={{ fontSize: '0.82rem' }}>
                      Executes <code style={{ background: 'rgba(59,130,246,0.15)', padding: '1px 5px', borderRadius: 4 }}>EXPLAIN</code> directly on your live database to show the query execution plan — scan type, rows examined, index usage, and estimated cost.
                    </span>
                  </div>
                </div>
              )}

              {inputMode === 'sql' && query.trim() && !query.trim().toUpperCase().startsWith('SELECT') && (
                <div className="notice notice-warning mt-4">
                  <HiOutlineExclamation className="notice-icon" />
                  <span>EXPLAIN only allowed for SELECT queries (read-only mode)</span>
                </div>
              )}

              {error && (
                <div className="notice notice-warning mt-4">
                  <HiOutlineExclamation className="notice-icon" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            <ResultPanel
              result={result}
              loading={loading}
              loadingText="Reading schemas & analyzing... This may take a moment for large databases 🔍"
            />
          </>
        )}
      </div>
    </div>
  )
}
