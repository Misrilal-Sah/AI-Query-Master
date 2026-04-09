"""
AI Query Master - RAG Pipeline
Supports two backends:
- ChromaDB (local persistent files)
- Supabase pgvector (hosted persistent vectors)
"""
import os
import math
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


def _env_flag(name: str, default: bool) -> bool:
    """Parse boolean-like environment variables."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class RAGPipeline:
    """RAG pipeline: load documents -> chunk -> embed -> store -> retrieve."""

    def __init__(self, knowledge_dir: str = None, chroma_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.getenv("RAG_KNOWLEDGE_DIR", "../RAG_Knowledge")
        self.chroma_dir = chroma_dir or os.getenv("CHROMA_DB_DIR", "./chroma_db")
        default_rag_enabled = not bool(os.getenv("RENDER"))
        self.enabled = _env_flag("RAG_ENABLED", default_rag_enabled)
        self.auto_index = _env_flag("RAG_AUTO_INDEX", True)
        self.embedding_dim = int(os.getenv("RAG_EMBEDDING_DIM", "384"))

        self.backend = (os.getenv("RAG_BACKEND") or ("supabase" if os.getenv("RENDER") else "chroma")).strip().lower()
        self.embedding_provider = (os.getenv("RAG_EMBEDDING_PROVIDER") or "auto").strip().lower()
        if self.embedding_provider == "auto":
            self.embedding_provider = "gemini" if os.getenv("GEMINI_API_KEY") else "local"

        self.collection = None
        self.supabase_client = None
        self.embedder = None
        self._initialized = False
        self.chunk_count = 0

    def _init_embedder(self):
        """Initialize embedding provider."""
        if self.embedding_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is required for RAG_EMBEDDING_PROVIDER=gemini")

            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.embedder = "gemini"
            logger.info("RAG embeddings provider: Gemini API")
            return

        if self.embedding_provider == "local":
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise RuntimeError(
                    "Local embedding provider requires sentence-transformers. "
                    "Install it or set RAG_EMBEDDING_PROVIDER=gemini with GEMINI_API_KEY."
                ) from e

            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("RAG embeddings provider: local sentence-transformers")
            return

        raise ValueError(f"Unknown RAG_EMBEDDING_PROVIDER: {self.embedding_provider}")

    def _init_storage(self):
        """Initialize selected vector storage backend."""
        if self.backend == "chroma":
            import chromadb

            client = chromadb.PersistentClient(path=self.chroma_dir)
            self.collection = client.get_or_create_collection(
                name="query_master_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"RAG backend: ChromaDB ({self.chroma_dir})")
            return

        if self.backend == "supabase":
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY are required for RAG_BACKEND=supabase")

            from supabase import create_client

            self.supabase_client = create_client(supabase_url, supabase_key)
            logger.info("RAG backend: Supabase pgvector")
            return

        raise ValueError(f"Unknown RAG_BACKEND: {self.backend}")

    def _count_chunks(self) -> int:
        """Count stored chunks in active backend."""
        if self.backend == "chroma":
            return self.collection.count() if self.collection is not None else 0

        if self.backend == "supabase":
            if self.supabase_client is None:
                return 0
            result = self.supabase_client.table("rag_chunks").select("id", count="exact").limit(1).execute()
            return result.count or 0

        return 0

    def initialize(self):
        """Initialize RAG pipeline and optionally index on first run."""
        if self._initialized:
            return

        if not self.enabled:
            logger.info("RAG is disabled via RAG_ENABLED=false")
            return

        logger.info("Initializing RAG pipeline...")

        try:
            self._init_embedder()
            self._init_storage()

            existing_count = self._count_chunks()
            self.chunk_count = existing_count
            logger.info(f"RAG store ready. Existing chunks: {existing_count}")

            if existing_count == 0:
                if self.auto_index:
                    self.index_knowledge_base()
                else:
                    logger.info("RAG store is empty; auto-index disabled (RAG_AUTO_INDEX=false)")

            self._initialized = True

        except Exception as e:
            logger.warning(f"RAG initialization failed; disabling RAG for this process: {e}")
            self.enabled = False

    def reset_index(self):
        """Clear all indexed knowledge chunks from active backend."""
        if not self.enabled:
            return

        if self.embedder is None or (self.collection is None and self.supabase_client is None):
            self._init_embedder()
            self._init_storage()

        if self.backend == "chroma":
            import chromadb

            client = chromadb.PersistentClient(path=self.chroma_dir)
            try:
                client.delete_collection("query_master_knowledge")
            except Exception:
                pass

            self.collection = client.get_or_create_collection(
                name="query_master_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.supabase_client.table("rag_chunks").delete().neq("id", "").execute()

        self.chunk_count = 0
        self._initialized = True

    def index_knowledge_base(self):
        """Index all documents from the knowledge directory."""
        if not self.enabled:
            logger.warning("RAG indexing skipped because RAG is disabled")
            return 0

        if self.embedder is None or (self.collection is None and self.supabase_client is None):
            self._init_embedder()
            self._init_storage()

        knowledge_path = Path(self.knowledge_dir).resolve()
        if not knowledge_path.exists():
            logger.warning(f"Knowledge directory not found: {knowledge_path}")
            return 0

        logger.info(f"Indexing knowledge base from: {knowledge_path}")

        all_chunks = []

        pdf_files = list(knowledge_path.rglob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        for pdf_file in pdf_files:
            all_chunks.extend(self._load_pdf(pdf_file))

        md_files = list(knowledge_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        for md_file in md_files:
            all_chunks.extend(self._load_markdown(md_file))

        txt_files = list(knowledge_path.rglob("*.txt"))
        for txt_file in txt_files:
            all_chunks.extend(self._load_text(txt_file))

        if not all_chunks:
            logger.warning("No documents found to index")
            return 0

        chunked = self._chunk_documents(all_chunks)
        logger.info(f"Created {len(chunked)} chunks from {len(all_chunks)} documents")

        self._store_chunks(chunked)

        self._initialized = True
        self.chunk_count = self._count_chunks()
        logger.info(f"Indexed chunks available: {self.chunk_count}")

        return self.chunk_count

    def _load_pdf(self, filepath: Path) -> List[Dict]:
        """Load and extract text from a PDF file."""
        try:
            import fitz

            doc = fitz.open(str(filepath))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            if text.strip():
                category = self._get_category(filepath)
                return [{
                    "text": text,
                    "source": filepath.name,
                    "category": category,
                    "type": "pdf",
                }]
        except Exception as e:
            logger.error(f"Error loading PDF {filepath}: {e}")
        return []

    def _load_markdown(self, filepath: Path) -> List[Dict]:
        """Load a markdown file."""
        try:
            text = filepath.read_text(encoding="utf-8")
            if text.strip():
                category = self._get_category(filepath)
                return [{
                    "text": text,
                    "source": filepath.name,
                    "category": category,
                    "type": "markdown",
                }]
        except Exception as e:
            logger.error(f"Error loading markdown {filepath}: {e}")
        return []

    def _load_text(self, filepath: Path) -> List[Dict]:
        """Load a text file."""
        try:
            text = filepath.read_text(encoding="utf-8")
            if text.strip():
                category = self._get_category(filepath)
                return [{
                    "text": text,
                    "source": filepath.name,
                    "category": category,
                    "type": "text",
                }]
        except Exception as e:
            logger.error(f"Error loading text {filepath}: {e}")
        return []

    def _get_category(self, filepath: Path) -> str:
        """Determine document category from file path."""
        path_str = str(filepath).lower()
        if "mysql" in path_str:
            return "mysql"
        if "postgres" in path_str or "postgresql" in path_str:
            return "postgresql"
        if "security" in path_str:
            return "security"
        if "index" in path_str:
            return "indexing"
        if "schema" in path_str:
            return "schema_design"
        if "optim" in path_str:
            return "optimization"
        return "general"

    def _chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Split documents into chunks."""
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        chunks = []
        for doc in documents:
            text_chunks = splitter.split_text(doc["text"])
            for i, chunk_text in enumerate(text_chunks):
                chunk_id = hashlib.md5(
                    f"{doc['source']}_{i}_{chunk_text[:50]}".encode()
                ).hexdigest()

                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "source": doc["source"],
                    "category": doc["category"],
                    "chunk_index": i,
                })

        return chunks

    def _normalize_embedding(self, values: List[float]) -> List[float]:
        """Normalize embedding vectors to configured dimensionality."""
        vec = [float(v) for v in values]
        if self.embedding_dim <= 0:
            return vec
        if len(vec) == self.embedding_dim:
            return vec
        if len(vec) > self.embedding_dim:
            return vec[:self.embedding_dim]
        return vec + [0.0] * (self.embedding_dim - len(vec))

    def _extract_embedding(self, response: Any) -> List[float]:
        """Extract embedding vector from Google Generative AI response shape."""
        if isinstance(response, dict):
            if "embedding" in response:
                return response["embedding"]
            if "embeddings" in response and response["embeddings"]:
                first = response["embeddings"][0]
                if isinstance(first, dict):
                    return first.get("values") or first.get("embedding") or []
                return first

        if hasattr(response, "embedding"):
            return response.embedding

        if hasattr(response, "embeddings") and response.embeddings:
            first = response.embeddings[0]
            if hasattr(first, "values"):
                return first.values
            if hasattr(first, "embedding"):
                return first.embedding

        return []

    def _embed_texts(self, texts: List[str], task_type: str) -> List[List[float]]:
        """Generate embeddings via configured provider."""
        if not texts:
            return []

        if self.embedding_provider == "gemini":
            import google.generativeai as genai

            output = []
            for text in texts:
                kwargs = {
                    "model": "models/text-embedding-004",
                    "content": text,
                    "task_type": task_type,
                }
                if self.embedding_dim > 0:
                    kwargs["output_dimensionality"] = self.embedding_dim

                try:
                    response = genai.embed_content(**kwargs)
                except TypeError:
                    kwargs.pop("output_dimensionality", None)
                    response = genai.embed_content(**kwargs)

                embedding = self._extract_embedding(response)
                if not embedding:
                    raise ValueError("Empty embedding response from Gemini")
                output.append(self._normalize_embedding(embedding))

            return output

        vectors = self.embedder.encode(texts)
        if hasattr(vectors, "tolist"):
            vectors = vectors.tolist()
        return [self._normalize_embedding(v) for v in vectors]

    def _store_chunks(self, chunks: List[Dict]):
        """Embed and store chunks in the selected backend."""
        batch_size = 100

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["text"] for c in batch]
            embeddings = self._embed_texts(texts, task_type="retrieval_document")

            if self.backend == "chroma":
                ids = [c["id"] for c in batch]
                metadatas = [{
                    "source": c["source"],
                    "category": c["category"],
                    "chunk_index": c["chunk_index"],
                } for c in batch]

                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                )
            else:
                rows = []
                for idx, chunk in enumerate(batch):
                    rows.append({
                        "id": chunk["id"],
                        "content": chunk["text"],
                        "source": chunk["source"],
                        "category": chunk["category"],
                        "chunk_index": chunk["chunk_index"],
                        "embedding": embeddings[idx],
                    })

                self.supabase_client.table("rag_chunks").upsert(rows, on_conflict="id").execute()

            logger.info(f"Stored batch {i // batch_size + 1} ({len(batch)} chunks)")

    def _category_filter(self, db_type: str) -> Optional[List[str]]:
        """Build category filter for query-time retrieval."""
        if db_type and db_type != "general":
            return [
                db_type.lower(),
                "general",
                "security",
                "indexing",
                "optimization",
                "schema_design",
            ]
        return None

    def _parse_embedding(self, value: Any) -> List[float]:
        """Parse embedding values returned from Supabase."""
        if isinstance(value, list):
            return [float(v) for v in value]

        if isinstance(value, dict):
            arr = value.get("values") or value.get("embedding") or []
            if isinstance(arr, list):
                return [float(v) for v in arr]
            return []

        if isinstance(value, str):
            text = value.strip()
            if text.startswith("[") and text.endswith("]"):
                text = text[1:-1]
            if not text:
                return []
            return [float(x.strip()) for x in text.split(",") if x.strip()]

        return []

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity for fallback search."""
        if not a or not b:
            return 0.0

        n = min(len(a), len(b))
        if n == 0:
            return 0.0

        dot = sum(a[i] * b[i] for i in range(n))
        norm_a = math.sqrt(sum(a[i] * a[i] for i in range(n)))
        norm_b = math.sqrt(sum(b[i] * b[i] for i in range(n)))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def _search_chroma(self, query_embedding: List[float], db_type: str, k: int) -> List[Dict]:
        """Retrieve candidates from ChromaDB backend."""
        where_filter = None
        categories = self._category_filter(db_type)
        if categories:
            where_filter = {"$or": [{"category": c} for c in categories]}

        fetch_k = min(k * 3, self.collection.count() or k * 3)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=fetch_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        candidates = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                score = 1 - results["distances"][0][i]
                candidates.append({
                    "text": doc,
                    "source": results["metadatas"][0][i].get("source", "unknown"),
                    "category": results["metadatas"][0][i].get("category", "general"),
                    "score": round(score, 4),
                })

        return candidates

    def _search_supabase(self, query_embedding: List[float], db_type: str, k: int) -> List[Dict]:
        """Retrieve candidates from Supabase pgvector backend."""
        categories = self._category_filter(db_type)
        fetch_k = max(k * 3, k)

        try:
            params = {
                "query_embedding": query_embedding,
                "match_count": fetch_k,
                "categories": categories,
            }
            rpc = self.supabase_client.rpc("match_rag_chunks", params).execute()
            rows = rpc.data or []
            if rows:
                return [{
                    "text": row.get("content", ""),
                    "source": row.get("source", "unknown"),
                    "category": row.get("category", "general"),
                    "score": round(float(row.get("similarity", 0.0)), 4),
                } for row in rows if row.get("content")]
        except Exception as e:
            logger.warning(f"Supabase RPC match_rag_chunks unavailable, falling back to client-side ranking: {e}")

        query = self.supabase_client.table("rag_chunks").select("content,source,category,embedding")
        if categories:
            query = query.in_("category", categories)

        rows = (query.limit(fetch_k * 4).execute().data or [])
        candidates = []

        for row in rows:
            embedding = self._normalize_embedding(self._parse_embedding(row.get("embedding")))
            if not embedding:
                continue
            score = self._cosine_similarity(query_embedding, embedding)
            candidates.append({
                "text": row.get("content", ""),
                "source": row.get("source", "unknown"),
                "category": row.get("category", "general"),
                "score": round(score, 4),
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:fetch_k]

    def _diversify(self, all_results: List[Dict], k: int) -> List[Dict]:
        """Diversify top-k to avoid single-source dominance."""
        selected = []
        source_counts = {}

        for r in all_results:
            src = r["source"]
            if source_counts.get(src, 0) < 2:
                selected.append(r)
                source_counts[src] = source_counts.get(src, 0) + 1
                if len(selected) >= k:
                    return selected

        if len(selected) < k:
            for r in all_results:
                if r not in selected:
                    selected.append(r)
                    if len(selected) >= k:
                        break

        return selected

    def search(
        self,
        query: str,
        db_type: str = "general",
        k: int = 5,
    ) -> List[Dict]:
        """Search the knowledge base for relevant chunks."""
        if not self.enabled:
            return []

        if not self._initialized:
            try:
                self.initialize()
            except Exception as e:
                logger.warning(f"RAG initialize failed during search: {e}")
                return []

        if not self._initialized or self.embedder is None:
            return []

        try:
            query_embedding = self._embed_texts([query], task_type="retrieval_query")[0]

            if self.backend == "supabase":
                all_results = self._search_supabase(query_embedding, db_type, k)
            else:
                all_results = self._search_chroma(query_embedding, db_type, k)

            search_results = self._diversify(all_results, k)

            source_count = len({r["source"] for r in search_results})
            logger.info(
                f"RAG search[{self.backend}]: '{query[:50]}...' -> {len(search_results)} results "
                f"from {source_count} sources"
            )
            return search_results

        except Exception as e:
            logger.warning(f"RAG search failed: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get non-intrusive RAG statistics (does not force initialization)."""
        return {
            "enabled": bool(self.enabled),
            "initialized": bool(self._initialized),
            "backend": self.backend,
            "embedding_provider": self.embedding_provider,
            "total_chunks": self.chunk_count if self._initialized else 0,
            "knowledge_dir": str(Path(self.knowledge_dir).resolve()),
            "chroma_dir": str(Path(self.chroma_dir).resolve()),
            "embedding_dim": self.embedding_dim,
        }


# Singleton
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the singleton RAG pipeline."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
