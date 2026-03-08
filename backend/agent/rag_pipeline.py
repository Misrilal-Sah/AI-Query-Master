"""
AI Query Master - RAG Pipeline
Loads PDFs and videos, chunks, embeds, and stores in ChromaDB.
"""
import os
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline: load documents → chunk → embed → store → retrieve."""

    def __init__(self, knowledge_dir: str = None, chroma_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.getenv("RAG_KNOWLEDGE_DIR", "../RAG_Knowledge")
        self.chroma_dir = chroma_dir or os.getenv("CHROMA_DB_DIR", "./chroma_db")
        self.collection = None
        self.embedder = None
        self._initialized = False
        self._init_failed = False

    def initialize(self):
        """Initialize the RAG pipeline (load embedder and ChromaDB)."""
        if self._initialized or self._init_failed:
            return

        logger.info("Initializing RAG pipeline...")

        try:
            # Initialize embedder
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

            # Initialize ChromaDB
            import chromadb
            from chromadb.config import Settings

            client = chromadb.PersistentClient(path=self.chroma_dir)

            # Get or create collection
            self.collection = client.get_or_create_collection(
                name="query_master_knowledge",
                metadata={"hnsw:space": "cosine"}
            )

            existing_count = self.collection.count()
            logger.info(f"ChromaDB initialized. Existing chunks: {existing_count}")

            # Index if empty
            if existing_count == 0:
                self.index_knowledge_base()

            self._initialized = True
        except Exception as e:
            logger.warning(f"RAG pipeline initialization failed (will work without RAG): {e}")
            self._init_failed = True

    def index_knowledge_base(self):
        """Index all documents from the knowledge directory."""
        knowledge_path = Path(self.knowledge_dir).resolve()
        if not knowledge_path.exists():
            logger.warning(f"Knowledge directory not found: {knowledge_path}")
            return 0

        logger.info(f"Indexing knowledge base from: {knowledge_path}")

        all_chunks = []

        # Process PDFs
        pdf_files = list(knowledge_path.rglob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        for pdf_file in pdf_files:
            chunks = self._load_pdf(pdf_file)
            all_chunks.extend(chunks)

        # Process markdown files
        md_files = list(knowledge_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        for md_file in md_files:
            chunks = self._load_markdown(md_file)
            all_chunks.extend(chunks)

        # Process text files
        txt_files = list(knowledge_path.rglob("*.txt"))
        for txt_file in txt_files:
            chunks = self._load_text(txt_file)
            all_chunks.extend(chunks)

        if not all_chunks:
            logger.warning("No documents found to index")
            return 0

        # Chunk the documents
        chunked = self._chunk_documents(all_chunks)
        logger.info(f"Created {len(chunked)} chunks from {len(all_chunks)} documents")

        # Embed and store
        self._store_chunks(chunked)
        logger.info(f"✓ Indexed {len(chunked)} chunks into ChromaDB")

        return len(chunked)

    def _load_pdf(self, filepath: Path) -> List[Dict]:
        """Load and extract text from a PDF file."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(str(filepath))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            if text.strip():
                # Determine category from path
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
        elif "postgres" in path_str or "postgresql" in path_str:
            return "postgresql"
        elif "security" in path_str:
            return "security"
        elif "index" in path_str:
            return "indexing"
        elif "schema" in path_str:
            return "schema_design"
        elif "optim" in path_str:
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

    def _store_chunks(self, chunks: List[Dict]):
        """Embed and store chunks in ChromaDB."""
        batch_size = 100

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            texts = [c["text"] for c in batch]
            ids = [c["id"] for c in batch]
            metadatas = [{
                "source": c["source"],
                "category": c["category"],
                "chunk_index": c["chunk_index"],
            } for c in batch]

            # Generate embeddings
            embeddings = self.embedder.encode(texts).tolist()

            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            logger.info(f"Stored batch {i // batch_size + 1} "
                         f"({len(batch)} chunks)")

    def search(
        self,
        query: str,
        db_type: str = "general",
        k: int = 5,
    ) -> List[Dict]:
        """
        Search the knowledge base for relevant chunks.
        Diversifies results to include multiple source documents.

        Args:
            query: The search query
            db_type: Filter by database type ('mysql', 'postgresql', 'general')
            k: Number of results to return

        Returns:
            List of dicts with 'text', 'source', 'category', 'score'
        """
        if not self._initialized:
            self.initialize()

        if self._init_failed or not self.embedder:
            logger.info("RAG not available, returning empty results")
            return []

        # Generate query embedding
        query_embedding = self.embedder.encode([query]).tolist()

        # Build where filter
        where_filter = None
        if db_type and db_type != "general":
            where_filter = {
                "$or": [
                    {"category": db_type.lower()},
                    {"category": "general"},
                    {"category": "security"},
                    {"category": "indexing"},
                    {"category": "optimization"},
                    {"category": "schema_design"},
                ]
            }

        # Fetch more results than needed, then diversify by source
        fetch_k = min(k * 3, self.collection.count() or k * 3)
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=fetch_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # Diversify: pick top results but limit max 2 per source
        all_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                score = 1 - results["distances"][0][i]
                all_results.append({
                    "text": doc,
                    "source": results["metadatas"][0][i].get("source", "unknown"),
                    "category": results["metadatas"][0][i].get("category", "general"),
                    "score": round(score, 4),
                })

        # Pick top-k with source diversity (max 2 chunks per source)
        search_results = []
        source_counts = {}
        for r in all_results:
            src = r["source"]
            if source_counts.get(src, 0) < 2:
                search_results.append(r)
                source_counts[src] = source_counts.get(src, 0) + 1
                if len(search_results) >= k:
                    break

        # If we didn't get enough, fill remaining regardless
        if len(search_results) < k:
            for r in all_results:
                if r not in search_results:
                    search_results.append(r)
                    if len(search_results) >= k:
                        break

        logger.info(f"RAG search: '{query[:50]}...' → {len(search_results)} results "
                     f"from {len(source_counts)} sources")
        return search_results

    def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        if not self._initialized:
            self.initialize()

        if self._init_failed or not self.collection:
            return {
                "total_chunks": 0,
                "knowledge_dir": str(Path(self.knowledge_dir).resolve()),
                "chroma_dir": str(Path(self.chroma_dir).resolve()),
                "status": "unavailable",
            }

        count = self.collection.count()
        return {
            "total_chunks": count,
            "knowledge_dir": str(Path(self.knowledge_dir).resolve()),
            "chroma_dir": str(Path(self.chroma_dir).resolve()),
        }


# Singleton
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the singleton RAG pipeline."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
