# chat/vector_store.py
import os
import json
import faiss
import numpy as np
import logging
from typing import List, Dict
from django.conf import settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector database with persistent docstore.
    - Embeddings: all-MiniLM-L6-v2 (384-dim)
    - Persists:
        - FAISS index to FAISS_INDEX_PATH
        - Doc metadata mapping to DOCSTORE_PATH
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dim: int = 384,
        index_path: str = None,
        docstore_path: str = None,
    ):
        self.model_name = model_name
        self.dim = dim
        self._embedder = None  # lazy init

        self.index_path = index_path or getattr(settings, "FAISS_INDEX_PATH", "faiss.index")
        self.docstore_path = docstore_path or getattr(settings, "DOCSTORE_PATH", "docstore.json")

        self.index = faiss.IndexFlatL2(self.dim)
        self.doc_store: Dict[str, Dict] = {}
        self.doc_order: List[str] = []

        # Initialize from persisted files if available
        self._load_docstore()
        self._rebuild_index()

    # --- Embedding ---
    @property
    def embedder(self):
        if self._embedder is None:
            logger.info("Loading embedding model: %s", self.model_name)
            self._embedder = SentenceTransformer(self.model_name)
        return self._embedder

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        vecs = self.embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vecs.astype("float32")

    # --- Persistence ---
    def _ensure_dir(self, path: str):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _save_docstore(self):
        self._ensure_dir(self.docstore_path)
        with open(self.docstore_path, "w", encoding="utf-8") as f:
            json.dump({"order": self.doc_order, "docs": self.doc_store}, f, ensure_ascii=False)

    def _load_docstore(self):
        if os.path.exists(self.docstore_path):
            with open(self.docstore_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.doc_order = data.get("order", [])
                self.doc_store = data.get("docs", {})
            logger.info("Loaded docstore with %d documents", len(self.doc_order))
        else:
            self.doc_order = []
            self.doc_store = {}

    def _save_index(self):
        self._ensure_dir(self.index_path)
        faiss.write_index(self.index, self.index_path)

    def _rebuild_index(self):
        """Rebuild FAISS index from docstore to ensure alignment."""
        self.index = faiss.IndexFlatL2(self.dim)
        if self.doc_order:
            contents = [self.doc_store[doc_id]["content"] for doc_id in self.doc_order if doc_id in self.doc_store]
            if contents:
                embeddings = self._embed_batch(contents)
                self.index.add(embeddings)
        self._save_index()

    # --- Public lifecycle ---
    def initialize_index(self):
        """
        Ensure the FAISS index and docstore are loaded and aligned.
        Called at app startup (ChatConfig.ready()).
        """
        try:
            self._load_docstore()
            self._rebuild_index()
            logger.info("VectorStore initialized with %d documents", len(self.doc_order))
        except Exception:
            logger.exception("Failed to initialize VectorStore")

    # --- Document Operations ---
    def document_exists(self, doc_id: str) -> bool:
        """Check if a document ID already exists in the store."""
        return doc_id in self.doc_store

    def add_documents(self, docs: List[Dict]) -> bool:
        """
        Add new documents to the vector store.
        Each doc must have: {"id", "title", "content", ...}
        """
        try:
            new_docs = [d for d in docs if d["id"] not in self.doc_store]
            if not new_docs:
                return True

            contents = [d.get("content", "") for d in new_docs]
            embeddings = self._embed_batch(contents)
            self.index.add(embeddings)

            for d in new_docs:
                self.doc_store[d["id"]] = d
                self.doc_order.append(d["id"])

            self._save_index()
            self._save_docstore()
            logger.info("Added %d documents to vector store", len(new_docs))
            return True
        except Exception:
            logger.exception("Error adding documents to vector store")
            return False

    def upsert_documents(self, docs: List[Dict]) -> bool:
        """
        Insert or update documents.
        """
        try:
            for d in docs:
                if d["id"] not in self.doc_store:
                    self.doc_order.append(d["id"])
                self.doc_store[d["id"]] = d

            self._rebuild_index()
            self._save_docstore()
            logger.info("Upserted %d documents", len(docs))
            return True
        except Exception:
            logger.exception("Error upserting documents")
            return False

    def reset(self):
        """Clear all documents and reset index."""
        self.index = faiss.IndexFlatL2(self.dim)
        self.doc_store = {}
        self.doc_order = []
        self._save_index()
        self._save_docstore()
        logger.info("Vector store reset")

    # --- Search ---
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for most relevant documents given a query string.
        Returns list of {"document": doc_dict, "score": similarity}
        """
        if not query.strip() or len(self.doc_order) == 0:
            return []

        try:
            q = self._embed_batch([query])
            distances, indices = self.index.search(q, min(top_k, len(self.doc_order)))

            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx < 0 or idx >= len(self.doc_order):
                    continue
                doc_id = self.doc_order[idx]
                results.append({
                    "document": self.doc_store[doc_id],
                    "score": 1 / (1 + float(dist)),  # similarity score
                })
            return results
        except Exception:
            logger.exception("Search failed")
            return []


# Singleton instance
vector_db = VectorStore()
