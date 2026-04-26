<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=AI%20Query%20Master&fontSize=60&fontColor=fff&animation=twinkling&fontAlignY=35&desc=AI%20Agentic%20Database%20Query%20Assistant&descAlignY=55&descSize=20" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

<br/>

[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Pro-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.1-F55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Multi--Model-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai)
[![MySQL](https://img.shields.io/badge/MySQL-Live%20Connect-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Live%20Connect-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

<br/>

> **The most powerful AI-driven SQL assistant** — review queries, analyze schemas, generate SQL from plain English, and connect to live databases with a full agentic AI pipeline featuring self-reflection and RAG-powered intelligence.

<br/>

[🚀 Quick Start](#-quick-start) · [☁️ Deploy](#deploy-render--supabase-pgvector) · [✨ Features](#-features) · [🏗️ Architecture](#️-system-architecture) · [🤖 AI Pipeline](#-ai-agent-pipeline) · [🛠️ Tech Stack](#️-tech-stack)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔍 Query Review
Paste any SQL query and get an instant AI-powered deep analysis — performance bottlenecks, security vulnerabilities, readability score, and concrete optimization suggestions with severity tags.

</td>
<td width="50%">

### 🗂️ Schema Review
Upload your DDL or paste a schema and receive a comprehensive evaluation of design choices, normalization gaps, missing indexes, and foreign key recommendations.

</td>
</tr>
<tr>
<td width="50%">

### 💬 Natural Language → SQL
Describe what you want in plain English. The AI understands your intent, picks the right dialect (MySQL / PostgreSQL), and returns a clean, optimized query with explanation.

</td>
<td width="50%">

### 🔌 Live Database Connection
Connect directly to your MySQL or PostgreSQL instance (read-only, session-based). Explore the live schema, run queries or NL prompts, and get EXPLAIN plan analysis — all in one place.

</td>
</tr>
<tr>
<td width="50%">

### 🖼️ Schema Builder
Upload a schema diagram image and the AI reverse-engineers it into complete SQL DDL — table definitions, constraints, indexes, and relationships included.

</td>
<td width="50%">

### 📜 Analysis History
Every analysis is saved. Search, filter by type, date, or database dialect, and revisit any past result with full detail view and re-analysis option.

</td>
</tr>
</table>

### Live Database — Bonus Capabilities

| Capability | Detail |
|---|---|
| 🔌 **Secure Connection** | Read-only, session-scoped — never modifies your data |
| 📊 **Schema Explorer** | Toggle panel with table count, expandable column details |
| 💬 **Dual Query Mode** | Switch between raw SQL and natural language on the fly |
| 🎙️ **Voice Input** | Speech-to-text for NL mode — just speak your question |
| 🤖 **Smart Context** | Agent automatically injects relevant schema context |
| 📋 **EXPLAIN Plans** | Run and visualize query execution plans instantly |

---

## 🏗️ System Architecture

```
╔══════════════════════════════════════════════════════════════╗
║                  React Frontend  (Vite + React 18)           ║
║   Dashboard │ Query Review │ Schema │ NL→SQL │ Live DB │ History ║
╚══════════════════════════╦═══════════════════════════════════╝
                           ║  REST API (HTTP/JSON)
                           ▼
╔══════════════════════════════════════════════════════════════╗
║                    FastAPI Backend                           ║
║  /api/review-query   /api/review-schema   /api/nl-to-query   ║
║  /api/connect-db     /api/history         /api/schema-build  ║
╚═══════════════╦══════════════════════╦═══════════════════════╝
                ║                      ║
                ▼                      ▼
╔══════════════════════╗  ╔══════════════════════════════════╗
║      AI Agent        ║  ║       Live DB Connection         ║
║  ┌────────────────┐  ║  ║  ┌───────────┐  ┌────────────┐  ║
║  │ Static Analysis│  ║  ║  │   MySQL   │  │ PostgreSQL │  ║
║  │ RAG Retrieval  │  ║  ║  │ (PyMySQL) │  │(Psycopg2)  │  ║
║  │ Tool Calling   │  ║  ║  └───────────┘  └────────────┘  ║
║  │ LLM Reasoning  │  ║  ║       Read-Only │ Session-Scoped ║
║  │ Self-Reflection│  ║  ╚══════════════════════════════════╝
║  │ Evaluation     │  ║
║  └───────┬────────┘  ║
╚══════════╬═══════════╝
           ║
     ╔═════╩══════╗
     ▼            ▼
╔═════════╗  ╔══════════╗
║ChromaDB ║  ║ Supabase ║
║  (RAG)  ║  ║(History) ║
╚═════════╝  ╚══════════╝
```

---

## 🤖 AI Agent Pipeline

Every analysis runs through a **fully agentic loop** — not a simple one-shot prompt:

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENTIC LOOP                            │
│                                                             │
│  📥 Input                                                   │
│      │                                                      │
│      ▼                                                      │
│  [1] 🔎 Static Analysis ──── Pattern-based issue detection  │
│      │                                                      │
│      ▼                                                      │
│  [2] 📚 RAG Retrieval ─────── ChromaDB knowledge search     │
│      │                                                      │
│      ▼                                                      │
│  [3] 🔧 Tool Calling ──────── Specialized analysis modules  │
│      │                                                      │
│      ▼                                                      │
│  [4] 🧠 LLM Reasoning ─────── Multi-model inference         │
│      │                                                      │
│      ▼                                                      │
│  [5] 🪞 Self-Reflection ───── Quality check (up to 3x)      │
│      │                                                      │
│      ▼                                                      │
│  [6] 📊 Evaluation ────────── Score: Perf│Sec│Read│Complex  │
│      │                                                      │
│      ▼                                                      │
│  📤 Final Response                                          │
└─────────────────────────────────────────────────────────────┘
```

### 🔀 Multi-LLM Fallback Chain

The agent automatically cascades through providers — **zero downtime if one fails**:

| # | Provider | Model | Speed | Notes |
|---|---|---|---|---|
| 1️⃣ | **Google Gemini** | `gemini-2.5-pro` | Fast | Primary — best quality |
| 2️⃣ | **Google Gemini** | `gemini-2.5-flash` | Faster | Flash fallback |
| 3️⃣ | **Groq** | `llama-3.1-8b-instant` | Ultra-fast | Low latency fallback |
| 4️⃣ | **OpenRouter** | `gemma-3-4b` (free) | Medium | Free tier fallback |
| 5️⃣ | **OpenRouter** | `llama-3.3-70b` (free) | Medium | Final free fallback |

---

## 🚀 Quick Start

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Node](https://img.shields.io/badge/Node.js-18%2B-green?style=flat-square&logo=node.js)
![Git](https://img.shields.io/badge/Git-required-orange?style=flat-square&logo=git)

### Step 1 — Clone & Setup Backend

```bash
git clone https://github.com/your-username/ai-query-master.git
cd "AI Query Master/backend"

# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux / macOS

# Install all dependencies
pip install -r requirements.txt
```

### Step 2 — Configure Environment

Create `backend/.env` and fill in your keys:

```env
# ── AI Providers ──────────────────────────────────────
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENROUTER_KEY_1=your_openrouter_key
OPENROUTER_KEY_2=your_openrouter_key_optional   # optional second key

# ── Supabase (Auth + History storage) ─────────────────
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
```

### Step 3 — Setup Supabase

Run [`migration.sql`](migration.sql) in your **Supabase SQL Editor** to create all required tables.

### Step 4 — Add Knowledge Base *(optional but recommended)*

Drop PDF documents into the RAG knowledge folders to supercharge analysis quality:

```
RAG_Knowledge/
├── Mysql/          ← MySQL best practices, docs, guides
└── PostgreSQL/     ← PostgreSQL best practices, docs, guides
```

### Step 5 — Launch

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
# ✅ API running at http://localhost:8000
# ✅ Docs available at http://localhost:8000/docs
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
# ✅ App running at http://localhost:5173
```

> Open [http://localhost:5173](http://localhost:5173) and start querying! 🎉

---

## Deploy: Render + Supabase pgvector

Use this production setup to avoid Render free-tier memory issues from local embedding models.

1. Create a new Supabase project and run [`migration.sql`](migration.sql) in SQL Editor.
2. Create a Render Web Service for backend:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Set backend environment variables in Render:

```env
# App
FRONTEND_URL=https://your-frontend.vercel.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# LLMs
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENROUTER_KEY_1=your_openrouter_key

# RAG (Supabase pgvector)
RAG_ENABLED=true
RAG_BACKEND=supabase
RAG_EMBEDDING_PROVIDER=gemini
RAG_EMBEDDING_DIM=384
RAG_PRELOAD_ON_STARTUP=false
RAG_AUTO_INDEX=false
```

4. Deploy backend, then call `POST /api/index` once to build embeddings and vectors.
5. Verify `GET /api/health` shows `rag_pipeline.backend = supabase` and non-zero chunks.
6. Ensure frontend points to your Render backend API URL (replace localhost in `frontend/src/api.js` for production).

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18 + Vite + React Router | SPA with fast HMR dev experience |
| **Backend** | FastAPI + Python 3.12 | Async REST API with auto-docs |
| **AI / LLM** | Gemini · Groq · OpenRouter | Multi-provider fallback inference |
| **RAG** | ChromaDB or Supabase pgvector · LangChain · Gemini Embeddings | Persistent vector search over knowledge base |
| **Auth & Storage** | Supabase | Auth, user management, history DB |
| **Live Database** | PyMySQL · Psycopg2 | Read-only live DB connections |

</div>

---

## 📁 Project Structure

```
AI Query Master/
│
├── 📂 backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── requirements.txt
│   ├── 📂 agent/
│   │   ├── agent.py             ← Agentic orchestration loop
│   │   ├── llm_provider.py      ← Multi-LLM fallback chain
│   │   ├── rag_pipeline.py      ← ChromaDB/Supabase pgvector RAG retrieval
│   │   ├── tools.py             ← Specialized analysis tools
│   │   ├── reflection.py        ← Self-reflection module
│   │   └── evaluator.py         ← Scoring: Perf/Sec/Read/Complex
│   ├── 📂 api/
│   │   ├── auth.py              ← Supabase auth endpoints
│   │   ├── nl_to_query.py       ← NL → SQL endpoint
│   │   ├── query_review.py      ← Query analysis endpoint
│   │   ├── schema_review.py     ← Schema analysis endpoint
│   │   ├── schema_builder.py    ← Image → DDL endpoint
│   │   ├── live_db.py           ← Live DB connection endpoint
│   │   └── history.py           ← Analysis history endpoint
│   └── 📂 db/
│       ├── mysql_connector.py   ← MySQL live connection
│       ├── postgres_connector.py← PostgreSQL live connection
│       └── supabase_client.py   ← Supabase client
│
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── 📂 pages/            ← Full-page route components
│   │   ├── 📂 components/       ← Reusable UI components
│   │   ├── 📂 context/          ← Auth & Theme context
│   │   └── api.js               ← Centralized API client
│   └── package.json
│
├── 📂 RAG_Knowledge/
│   ├── Mysql/                   ← MySQL knowledge documents
│   └── PostgreSQL/              ← PostgreSQL knowledge documents
│
└── migration.sql                ← Supabase schema setup
```

---

## 🔐 Security Model

- **Live DB connections** are strictly **read-only** and **session-scoped** — no write operations, no persistent credentials stored
- All API keys are loaded from environment variables — never hardcoded
- Authentication handled by Supabase with JWT tokens
- RAG supports local (ChromaDB) or hosted (Supabase pgvector) storage for indexed chunks

---

<div align="center">

### ⭐ If this project helps you, give it a star!

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer" width="100%"/>

</div>
