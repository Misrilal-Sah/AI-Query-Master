# AI Query Master — AI Agentic Database Query Assistant

An intelligent AI agent system that helps developers **analyze, optimize, and generate database queries** across MySQL and PostgreSQL.

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Query Review** | Analyze SQL queries for performance, security, and readability with AI scoring |
| **Schema Review** | Evaluate database schema design and suggest improvements |
| **NL to Query** | Convert natural language to optimized SQL queries |
| **Live Database** | Connect to a real database for schema inspection, EXPLAIN plans, and AI analysis |
| **Schema Builder** | Upload a schema diagram image and get SQL DDL generated automatically |
| **Analysis History** | View, filter, and revisit all past query analyses |

### Live Database Tool Features
- 🔌 Connect to MySQL (read-only, session-based)
- 📊 Toggleable schema explorer (shows table count, expandable)
- 💬 SQL Query mode + Natural Language mode
- 🎙️ Speech-to-text input (NL mode only)
- 🤖 AI Agent analysis with smart schema context
- 📋 EXPLAIN plan execution

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│           React Frontend (Vite)              │
│  Dashboard │ Query │ Schema │ NL │ Live DB   │
└────────────────────┬─────────────────────────┘
                     │ REST API
                     ▼
┌──────────────────────────────────────────────┐
│           FastAPI Backend                     │
│  /api/review-query │ /api/review-schema      │
│  /api/nl-to-query  │ /api/connect-db         │
└────────────────────┬─────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   AI Agent       │    │  Live DB Conn   │
│  • Multi-LLM     │    │  • MySQL        │
│  • RAG Pipeline   │    │  • PostgreSQL   │
│  • Tool Calling   │    │  (Read-only)    │
│  • Self-Reflection│    └─────────────────┘
│  • Evaluation     │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ChromaDB│ │ Supabase │
│ (RAG)  │ │ (History)│
└────────┘ └──────────┘
```

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

Edit `backend/.env` with your API keys:

```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OPENROUTER_KEY_1=your_key
OPENROUTER_KEY_2=your_key_optional
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

### 3. Setup Supabase

Run `migration.sql` in your Supabase SQL Editor.

### 4. Add Knowledge Base

Place PDF/videos documents in:
- `RAG_Knowledge/Mysql/`
- `RAG_Knowledge/PostgreSQL/`

### 5. Start Backend

```bash
cd backend
venv\Scripts\activate
python main.py
# Server runs at http://localhost:8000
```

### 6. Start Frontend

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:5173
```

## 🤖 AI Agent Pipeline

Each analysis follows this agentic loop:

1. **Static Analysis** → Pattern-based issue detection
2. **RAG Retrieval** → Search knowledge base for best practices
3. **Tool Calling** → Run specialized analysis tools
4. **LLM Reasoning** → Generate comprehensive review
5. **Self-Reflection** → Evaluate and improve response (up to 3 iterations)
6. **Evaluation** → Score on Performance, Security, Readability, Complexity

### Multi-LLM Fallback Chain

| Priority | Provider | Model |
|----------|----------|-------|
| 1 | Gemini | 2.5 Pro |
| 2 | Gemini | 2.5 Flash |
| 3 | Groq | Llama 3.1 8B Instant |
| 4 | OpenRouter | Gemma 3 4B (free) |
| 5 | OpenRouter | Llama 3.3 70B (free) |

## 📁 Project Structure

```
├── backend/
│   ├── main.py              
│   ├── agent/               
│   │   ├── llm_provider.py  
│   │   ├── rag_pipeline.py  
│   │   ├── tools.py         
│   │   ├── reflection.py    
│   │   ├── evaluator.py     
│   │   └── agent.py         
│   ├── api/                 
│   └── db/                  
├── frontend/
│   ├── src/
│   │   ├── pages/           
│   │   ├── components/      
│   │   └── index.css        
│   └── package.json
├── RAG_Knowledge/           
└── migration.sql   
```

## 🛠️ Technologies

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, React Router |
| Backend | FastAPI, Python 3.12 |
| AI/LLM | Gemini, Groq, OpenRouter |
| RAG | ChromaDB, LangChain, SentenceTransformers |
| Database | PostgreSQL |
| Live DB | PyMySQL, Psycopg2 |



