import { useState, useRef } from 'react'
import { HiOutlineChatAlt2, HiOutlinePlay, HiOutlineLightningBolt, HiOutlineMicrophone } from 'react-icons/hi'
import DatabaseSelector from '../components/DatabaseSelector'
import ResultPanel from '../components/ResultPanel'
import api from '../api'

const quickPrompts = [
  "Show top 10 users by total order value",
  "Find all users who haven't placed an order in 30 days",
  "Get monthly revenue for the last 12 months",
  "List products with less than 10 items in stock",
  "Find duplicate email addresses in the users table",
]

export default function NLToQuery() {
  const [description, setDescription] = useState('')
  const [dbType, setDbType] = useState('mysql')
  const [schemaContext, setSchemaContext] = useState('')
  const [showSchema, setShowSchema] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [listening, setListening] = useState(false)
  const recognitionRef = useRef(null)

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      setDescription(prev => {
        // Replace interim with final
        const lastFinal = event.results[event.results.length - 1]
        if (lastFinal.isFinal) {
          return prev + transcript + ' '
        }
        return prev
      })
    }

    recognition.onend = () => {
      setListening(false)
      recognitionRef.current = null
    }

    recognition.onerror = (e) => {
      setListening(false)
      if (e.error !== 'aborted') {
        setError(`Speech error: ${e.error}`)
      }
    }

    recognitionRef.current = recognition
    recognition.start()
    setListening(true)
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    setListening(false)
  }

  const handleSubmit = async () => {
    if (!description.trim()) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await api.post('/nl-to-query', {
        description: description.trim(),
        db_type: dbType,
        schema_context: schemaContext.trim() || undefined,
      })
      setResult(response.data)
    } catch (err) {
      setError(err.message || 'Query generation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <HiOutlineChatAlt2 className="icon" />
          Natural Language to Query
        </h1>
        <p className="page-subtitle">
          Describe what you need in plain English (or use voice 🎙️) and get an optimized SQL query
        </p>
      </div>

      <div className="flex-col gap-4" style={{ display: 'flex' }}>
        <div className="glass-card">
          <div className="form-label mb-4">Database Type</div>
          <DatabaseSelector value={dbType} onChange={setDbType} />

          <div className="form-group mt-4">
            <label className="form-label">Describe Your Query</label>
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <textarea
                className="textarea"
                placeholder="Describe what data you want to retrieve in plain English..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                style={{ minHeight: 100, flex: 1 }}
              />
              <button
                className={`mic-btn ${listening ? 'listening' : ''}`}
                onClick={listening ? stopListening : startListening}
                title={listening ? 'Stop listening' : 'Start voice input'}
              >
                <HiOutlineMicrophone />
              </button>
            </div>
            {listening && (
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-red)', display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                <span className="status-dot" style={{ background: 'var(--accent-red)' }} />
                Listening... speak now
              </div>
            )}
          </div>

          {/* Quick Prompts */}
          <div className="mt-2">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>
              Quick prompts:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {quickPrompts.map((prompt, i) => (
                <button
                  key={i}
                  className="btn btn-ghost btn-sm"
                  onClick={() => setDescription(prompt)}
                  style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                >
                  <HiOutlineLightningBolt style={{ fontSize: '0.7rem' }} />
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Optional Schema Context */}
          <div className="mt-4">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setShowSchema(!showSchema)}
            >
              {showSchema ? '▾ Hide Schema Context' : '▸ Add Schema Context (optional)'}
            </button>
            {showSchema && (
              <div className="form-group mt-2">
                <label className="form-label">Schema Context</label>
                <textarea
                  className="textarea"
                  placeholder="Paste your CREATE TABLE statements here to help the AI generate more accurate queries..."
                  value={schemaContext}
                  onChange={(e) => setSchemaContext(e.target.value)}
                  style={{ minHeight: 100 }}
                />
              </div>
            )}
          </div>

          <div className="mt-4" style={{ display: 'flex', gap: 12 }}>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleSubmit}
              disabled={loading || !description.trim()}
            >
              <HiOutlinePlay />
              {loading ? 'Generating...' : 'Generate Query'}
            </button>
            {description && (
              <button className="btn btn-ghost" onClick={() => { setDescription(''); setResult(null); setError(''); }}>
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
