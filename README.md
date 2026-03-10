# AI Query Master — AI Agentic Database Query Assistant

An intelligent AI agent system that helps developers **analyze and optimize MySQL database queries and schemas**.

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Query Review** | Analyze SQL queries for performance, security, and readability with AI scoring |
| **Schema Review** | Evaluate database schema design and suggest improvements |

## 🏗️ Architecture

> See [`architecture.mmd`](./architecture.mmd) for the full Mermaid diagram.

```
┌──────────────────────────────────────────┐
│         React Frontend (Vite)            │
│  Dashboard  │  Query Review  │  Schema   │
└──────────────────┬───────────────────────┘
                   │ REST API
                   ▼
┌──────────────────────────────────────────┐
│         FastAPI Backend                  │
│  /api/review-query  │  /api/review-schema│
└──────────────────┬───────────────────────┘
                   │
         ┌─────────┘
         ▼
┌─────────────────┐
│   AI Agent       │
│  • Multi-LLM     │
│  • RAG Pipeline  │
│  • Tool Calling  │
│  • Self-Reflection│
│  • Evaluation    │
└────────┬────────┘
         │
         ▼
┌────────────────┐
│   ChromaDB     │
│  (RAG Store)   │
└────────────────┘
```

## 🤖 AI Agent Pipeline

Each analysis follows this agentic loop:

1. **Static Analysis** → Pattern-based issue detection
2. **RAG Retrieval** → Search knowledge base for best practices
3. **Tool Calling** → Run specialized analysis tools
4. **LLM Reasoning** → Generate comprehensive review
5. **Self-Reflection** → Evaluate and improve response (up to 2 iterations)
6. **Evaluation** → Score on Performance, Security, Readability, Complexity

### Multi-LLM Fallback Chain

| Priority | Provider | Model |
|----------|----------|-------|
| 1 | Gemini | 2.0 Flash |
| 2 | Gemini | 2.0 Flash Lite |
| 3 | Groq | Llama 3.1 8B Instant |
| 4 | OpenRouter | Gemma 3 4B (free) |
| 5 | OpenRouter | Llama 3.3 70B (free) |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### 1. Clone & Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env` with your API keys:

```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OPENROUTER_KEY_1=your_key
OPENROUTER_KEY_2=your_key_optional
```

### 3. Add Knowledge Base

Place PDF/markdown documents in:
- `RAG_Knowledge/Mysql/`

### 4. Start Backend

```bash
cd backend
venv\Scripts\activate
python main.py
# Server runs at http://localhost:8000
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:5173
```

## 📁 Project Structure

```
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # API keys (not committed)
│   ├── agent/
│   │   ├── agent.py             # Main agent orchestrator
│   │   ├── llm_provider.py      # Multi-LLM fallback chain
│   │   ├── rag_pipeline.py      # RAG: load, chunk, embed, search
│   │   ├── tools.py             # Static analysis tools
│   │   ├── reflection.py        # Self-reflection engine
│   │   └── evaluator.py         # Scoring system
│   ├── api/
│   │   ├── query_review.py      # POST /api/review-query
│   │   └── schema_review.py     # POST /api/review-schema
│   └── utils/
│       └── helpers.py           # Utility functions
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component & routing
│   │   ├── api.js               # Axios API client
│   │   ├── main.jsx             # React entry point
│   │   ├── index.css            # Global styles & design system
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Home page with feature cards
│   │   │   ├── Dashboard.css    # Dashboard styles
│   │   │   ├── QueryReview.jsx  # Query analysis page
│   │   │   └── SchemaReview.jsx # Schema analysis page
│   │   ├── components/
│   │   │   ├── Sidebar.jsx      # Navigation sidebar
│   │   │   ├── Sidebar.css      # Sidebar styles
│   │   │   ├── DatabaseSelector.jsx  # MySQL/PostgreSQL selector
│   │   │   └── ResultPanel.jsx  # AI analysis results display
│   │   └── context/
│   │       └── ThemeContext.jsx  # Dark/light theme toggle
│   └── package.json
└── RAG_Knowledge/               # PDF & markdown knowledge base
```

## 🛠️ Technologies

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, React Router |
| Database | MySQL |
| Backend | FastAPI, Python 3.12 |
| AI/LLM | Gemini, Groq, OpenRouter |
| RAG | ChromaDB, LangChain, SentenceTransformers |
| PDF Processing | PyMuPDF |
