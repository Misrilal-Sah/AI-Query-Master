import { Link } from 'react-router-dom'
import { HiOutlineCode, HiOutlineDatabase, HiOutlineChatAlt2, HiOutlineServer, HiOutlineLightningBolt, HiOutlineShieldCheck, HiOutlineChartBar, HiOutlinePhotograph } from 'react-icons/hi'
import './Dashboard.css'

const features = [
  {
    path: '/query-review',
    icon: HiOutlineCode,
    title: 'Query Review',
    description: 'Analyze SQL queries for performance, security, and readability issues',
    gradient: 'linear-gradient(135deg, #3b82f6, #6366f1)',
  },
  {
    path: '/schema-review',
    icon: HiOutlineDatabase,
    title: 'Schema Review',
    description: 'Evaluate database schema design and suggest improvements',
    gradient: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
  },
  {
    path: '/schema-builder',
    icon: HiOutlinePhotograph,
    title: 'Schema Builder',
    description: 'Upload a diagram image and generate SQL DDL automatically',
    gradient: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
  },
  {
    path: '/nl-to-query',
    icon: HiOutlineChatAlt2,
    title: 'NL to Query',
    description: 'Convert natural language descriptions into optimized SQL queries',
    gradient: 'linear-gradient(135deg, #10b981, #06b6d4)',
  },
  {
    path: '/live-db',
    icon: HiOutlineServer,
    title: 'Live Database',
    description: 'Connect to a database and analyze real schemas with EXPLAIN plans',
    gradient: 'linear-gradient(135deg, #f59e0b, #ef4444)',
  },
]

const capabilities = [
  { icon: HiOutlineLightningBolt, label: 'Multi-LLM Fallback', desc: 'Gemini → Groq → OpenRouter' },
  { icon: HiOutlineShieldCheck, label: 'RAG Knowledge Base', desc: 'Best practices retrieval' },
  { icon: HiOutlineChartBar, label: 'Self-Reflection', desc: 'Iterative quality improvement' },
]

export default function Dashboard() {
  return (
    <div className="dashboard animate-fade-in">
      {/* Hero */}
      <div className="dashboard-hero">
        <div className="hero-badge">AI-Powered Database Assistant</div>
        <h1 className="hero-title">
          <span className="gradient-text">AI Query Master</span>
        </h1>
        <p className="hero-subtitle">
          Analyze, optimize, and generate database queries with intelligent AI agents.
          Powered by RAG, self-reflection, and multi-LLM reasoning.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="features-grid">
        {features.map((feature) => (
          <Link key={feature.path} to={feature.path} className="feature-card">
            <div className="feature-icon" style={{ background: feature.gradient }}>
              <feature.icon />
            </div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-desc">{feature.description}</p>
            <span className="feature-cta">Get started →</span>
          </Link>
        ))}
      </div>

      {/* Capabilities */}
      <div className="capabilities-section">
        <h2 className="section-title">Agent Capabilities</h2>
        <div className="capabilities-grid">
          {capabilities.map((cap, i) => (
            <div key={i} className="capability-card glass-card">
              <cap.icon className="capability-icon" />
              <div>
                <div className="capability-label">{cap.label}</div>
                <div className="capability-desc">{cap.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
