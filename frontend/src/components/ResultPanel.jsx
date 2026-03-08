import { useState } from 'react'
import { HiOutlineClipboardCopy, HiOutlineCheck, HiOutlinePlus, HiOutlineMinus } from 'react-icons/hi'

function CollapsibleSection({ title, children, defaultOpen = true, count, headerRight }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="glass-card collapsible-section">
      <button className="collapsible-header" onClick={() => setOpen(!open)}>
        <div className="collapsible-left">
          <span className="collapsible-toggle">
            {open ? <HiOutlineMinus /> : <HiOutlinePlus />}
          </span>
          <h3 className="collapsible-title">
            {title}
            {count !== undefined && <span className="collapsible-count">({count})</span>}
          </h3>
        </div>
        {headerRight && <div className="collapsible-right" onClick={e => e.stopPropagation()}>{headerRight}</div>}
      </button>
      {open && <div className="collapsible-body">{children}</div>}
    </div>
  )
}

export default function ResultPanel({ result, loading, loadingText }) {
  const [copiedField, setCopiedField] = useState(null)

  if (loading) {
    return (
      <div className="glass-card">
        <div className="spinner-container">
          <div className="spinner" />
          <div className="spinner-text">{loadingText || 'AI Agent is analyzing...'}</div>
          {result?.steps && (
            <div className="steps-timeline mt-4">
              {result.steps.map((step, i) => (
                <div key={i} className={`step-item step-${step.status}`}>
                  <div className="step-number">{step.step}</div>
                  <span className="step-action">{step.action}</span>
                  {step.result && <span className="step-result">{step.result}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (!result) return null

  const copyToClipboard = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedField(field)
      setTimeout(() => setCopiedField(null), 2000)
    } catch (err) {
      console.error('Copy failed:', err)
    }
  }

  return (
    <div className="result-panel animate-fade-in flex-col gap-4" style={{ display: 'flex' }}>
      {/* Scores */}
      {result.scores && (
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-heading)' }}>
              Evaluation Scores
            </h3>
            {result.scores.grade && (
              <div className={`grade-badge grade-${result.scores.grade}`}>
                {result.scores.grade}
              </div>
            )}
          </div>
          <div className="scores-grid">
            {result.scores.performance_score !== undefined && (
              <ScoreCard label="Performance" value={result.scores.performance_score} />
            )}
            {result.scores.security_score !== undefined && (
              <ScoreCard label="Security" value={result.scores.security_score} />
            )}
            {result.scores.readability_score !== undefined && (
              <ScoreCard label="Readability" value={result.scores.readability_score} />
            )}
            {result.scores.complexity_score !== undefined && (
              <ScoreCard label="Complexity" value={result.scores.complexity_score} />
            )}
            {result.scores.design_score !== undefined && (
              <ScoreCard label="Design" value={result.scores.design_score} />
            )}
            {result.scores.overall_score !== undefined && (
              <ScoreCard label="Overall" value={result.scores.overall_score} />
            )}
          </div>
        </div>
      )}

      {/* Agent Process — collapsible, default OPEN */}
      {result.steps && (
        <CollapsibleSection
          title="Agent Process"
          defaultOpen={true}
          headerRight={
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.85rem' }}>
              {result.confidence !== undefined && (
                <span style={{ color: result.confidence >= 70 ? 'var(--accent-green)' : 'var(--accent-orange)' }}>
                  Confidence: {result.confidence}%
                </span>
              )}
              {result.provider && (
                <span style={{ color: 'var(--text-muted)' }}>via {result.provider}</span>
              )}
              {result.time_seconds && (
                <span style={{ color: 'var(--text-muted)' }}>{result.time_seconds}s</span>
              )}
            </div>
          }
        >
          <div className="steps-timeline">
            {result.steps.map((step, i) => (
              <div key={i} className={`step-item step-${step.status}`}>
                <div className="step-number">✓</div>
                <span className="step-action">{step.action}</span>
                {step.result && <span className="step-result">{step.result}</span>}
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* Static Analysis Issues — collapsible, default OPEN */}
      {result.static_issues && result.static_issues.length > 0 && (
        <CollapsibleSection
          title="Static Analysis Issues"
          defaultOpen={true}
          count={result.static_issues.length}
        >
          <div className="flex-col gap-2" style={{ display: 'flex' }}>
            {result.static_issues.map((issue, i) => (
              <div key={i} className="issue-item" style={{
                padding: '10px 14px',
                background: 'var(--bg-nested)',
                borderRadius: 'var(--radius-sm)',
                borderLeft: `3px solid ${
                  issue.severity === 'critical' ? 'var(--accent-red)' :
                  issue.severity === 'warning' ? 'var(--accent-orange)' :
                  'var(--accent-blue)'
                }`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span className={`issue-tag issue-${issue.severity}`}>
                    {issue.severity}
                  </span>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{issue.title}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
                  {issue.description}
                </p>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* AI Analysis — collapsible, default CLOSED */}
      {result.analysis && (
        <CollapsibleSection
          title="AI Analysis"
          defaultOpen={false}
          headerRight={
            <button
              className={`copy-btn ${copiedField === 'analysis' ? 'copied' : ''}`}
              onClick={() => copyToClipboard(result.analysis, 'analysis')}
              style={{ position: 'static' }}
            >
              {copiedField === 'analysis' ? (
                <><HiOutlineCheck /> Copied!</>
              ) : (
                <><HiOutlineClipboardCopy /> Copy</>
              )}
            </button>
          }
        >
          <div className="markdown-content" style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem', lineHeight: 1.7 }}>
            {result.analysis}
          </div>
        </CollapsibleSection>
      )}

      {/* Sources */}
      {result.sources && result.sources.length > 0 && (
        <div className="glass-card">
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-heading)' }}>
            Knowledge Sources
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {[...new Set(result.sources)].map((source, i) => (
              <span key={i} className="source-tag">
                📄 {source}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ScoreCard({ label, value }) {
  const scoreClass = value >= 80 ? 'score-good' : value >= 60 ? 'score-fair' : 'score-poor'
  return (
    <div className={`score-card ${scoreClass}`}>
      <div className="score-value">{value}</div>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${value}%` }} />
      </div>
      <div className="score-label">{label}</div>
    </div>
  )
}
