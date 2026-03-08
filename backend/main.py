"""
AI Query Master - FastAPI Application Entry Point
"""
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize on startup, cleanup on shutdown."""
    logger.info("=" * 60)
    logger.info("  AI Query Master - Starting Up")
    logger.info("=" * 60)

    # Initialize RAG pipeline
    try:
        from agent.rag_pipeline import get_rag_pipeline
        rag = get_rag_pipeline()
        rag.initialize()
        stats = rag.get_stats()
        logger.info(f"RAG Pipeline: {stats['total_chunks']} chunks indexed")
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")

    # Initialize LLM provider
    try:
        from agent.llm_provider import get_llm_provider
        llm = get_llm_provider()
        logger.info(f"LLM Provider: {len(llm.providers)} providers available")
    except Exception as e:
        logger.error(f"LLM initialization failed: {e}")

    # Initialize Supabase
    try:
        from db.supabase_client import get_supabase_client
        sb = get_supabase_client()
        logger.info(f"Supabase: {'Connected' if sb.is_available else 'Not configured'}")
    except Exception as e:
        logger.warning(f"Supabase initialization: {e}")

    logger.info("=" * 60)
    logger.info("  AI Query Master - Ready!")
    logger.info("=" * 60)

    yield  # App is running

    # Shutdown
    logger.info("AI Query Master - Shutting Down")


# Create FastAPI app
app = FastAPI(
    title="AI Query Master",
    description="AI Agentic Database Query Assistant — Analyze, optimize, and generate database queries",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from api.query_review import router as query_review_router
from api.schema_review import router as schema_review_router
from api.nl_to_query import router as nl_to_query_router
from api.live_db import router as live_db_router
from api.history import router as history_router
from api.auth import router as auth_router
from api.schema_builder import router as schema_builder_router
from api.email_templates import router as email_templates_router

app.include_router(query_review_router)
app.include_router(schema_review_router)
app.include_router(nl_to_query_router)
app.include_router(live_db_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(schema_builder_router)
app.include_router(email_templates_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "AI Query Master",
        "version": "1.0.0",
        "status": "running",
        "description": "AI Agentic Database Query Assistant",
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    from agent.rag_pipeline import get_rag_pipeline
    from agent.llm_provider import get_llm_provider
    from db.supabase_client import get_supabase_client

    rag = get_rag_pipeline()
    llm = get_llm_provider()
    sb = get_supabase_client()

    return {
        "status": "healthy",
        "components": {
            "rag_pipeline": {
                "status": "ready" if rag._initialized else "not_initialized",
                "chunks": rag.collection.count() if rag._initialized else 0,
            },
            "llm_provider": {
                "status": "ready",
                "providers": [p["name"] for p in llm.providers],
            },
            "supabase": {
                "status": "connected" if sb.is_available else "not_configured",
            },
        },
    }


@app.post("/api/index")
async def reindex_knowledge_base():
    """Re-index the RAG knowledge base."""
    from agent.rag_pipeline import get_rag_pipeline

    rag = get_rag_pipeline()

    # Clear existing
    import chromadb
    client = chromadb.PersistentClient(path=rag.chroma_dir)
    try:
        client.delete_collection("query_master_knowledge")
    except Exception:
        pass

    rag.collection = client.get_or_create_collection(
        name="query_master_knowledge",
        metadata={"hnsw:space": "cosine"}
    )

    count = rag.index_knowledge_base()

    return {
        "success": True,
        "message": f"Indexed {count} chunks",
        "total_chunks": count,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
