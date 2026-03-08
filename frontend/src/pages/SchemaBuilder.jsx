import { useState, useRef } from 'react'
import { HiOutlinePhotograph, HiOutlinePlay, HiOutlineX, HiOutlineUpload, HiOutlineClipboardCopy, HiOutlineCheck } from 'react-icons/hi'
import DatabaseSelector from '../components/DatabaseSelector'
import api from '../api'

export default function SchemaBuilder() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dbType, setDbType] = useState('mysql')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  const handleFile = (file) => {
    if (!file) return
    const allowed = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
    if (!allowed.includes(file.type)) {
      setError('Please upload a PNG, JPG, or WebP image')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be under 10MB')
      return
    }
    setImage(file)
    setPreview(URL.createObjectURL(file))
    setError('')
    setResult(null)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleSubmit = async () => {
    if (!image) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('image', image)
      formData.append('db_type', dbType)

      const response = await api.post('/build-schema', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(response.data)
    } catch (err) {
      setError(err.message || 'Schema generation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (result?.schema) {
      await navigator.clipboard.writeText(result.schema)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const clearImage = () => {
    setImage(null)
    setPreview(null)
    setResult(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">
          <HiOutlinePhotograph className="icon" />
          Schema Builder
        </h1>
        <p className="page-subtitle">
          Upload a schema diagram image and get SQL DDL generated automatically
        </p>
      </div>

      <div className="flex-col gap-4" style={{ display: 'flex' }}>
        <div className="glass-card">
          <div className="form-label mb-4">Target Database</div>
          <DatabaseSelector value={dbType} onChange={setDbType} />

          <div className="form-group mt-4">
            <label className="form-label">Schema Diagram</label>

            {!preview ? (
              <div
                className={`upload-zone ${dragOver ? 'dragover' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
              >
                <div className="upload-icon">
                  <HiOutlineUpload />
                </div>
                <div className="upload-text">
                  Drop your schema diagram here or <strong>click to browse</strong>
                </div>
                <div className="upload-hint">
                  Supports PNG, JPG, WebP • Max 10MB
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  onChange={(e) => handleFile(e.target.files[0])}
                  style={{ display: 'none' }}
                />
              </div>
            ) : (
              <div className="upload-preview">
                <img src={preview} alt="Schema diagram" />
                <button className="btn btn-danger btn-sm remove-btn" onClick={clearImage}>
                  <HiOutlineX /> Remove
                </button>
              </div>
            )}
          </div>

          <button
            className="btn btn-primary btn-lg mt-4"
            onClick={handleSubmit}
            disabled={loading || !image}
          >
            <HiOutlinePlay />
            {loading ? 'Generating Schema...' : 'Generate DDL'}
          </button>

          {error && (
            <div className="notice notice-warning mt-4">
              <span className="notice-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Result */}
        {loading && (
          <div className="glass-card">
            <div className="spinner-container">
              <div className="spinner" />
              <div className="spinner-text">AI is analyzing your schema diagram...</div>
            </div>
          </div>
        )}

        {result && (
          <div className="glass-card animate-fade-in">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-heading)' }}>
                Generated Schema ({dbType === 'mysql' ? 'MySQL' : 'PostgreSQL'})
              </h3>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className={`copy-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
                  {copied ? <><HiOutlineCheck /> Copied!</> : <><HiOutlineClipboardCopy /> Copy DDL</>}
                </button>
              </div>
            </div>

            <pre style={{
              background: 'var(--bg-nested)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              padding: 20,
              overflow: 'auto',
              maxHeight: 500,
              fontFamily: 'var(--font-mono)',
              fontSize: '0.85rem',
              lineHeight: 1.6,
              color: 'var(--text-primary)',
            }}>
              {result.schema}
            </pre>

            {result.analysis && (
              <div className="mt-4">
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-heading)', marginBottom: 8 }}>
                  Schema Notes
                </h4>
                <div className="markdown-content" style={{ fontSize: '0.85rem', whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>
                  {result.analysis}
                </div>
              </div>
            )}

            {result.provider && (
              <div style={{ marginTop: 12, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Generated via {result.provider} in {result.time_seconds}s
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
