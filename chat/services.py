import time
import logging
from typing import List, Dict
from documents.models import Document
from .vector_store import vector_db
from .ai_service import ai_service

logger = logging.getLogger(__name__)


class AdvancedRAGService:
    """Advanced RAG service with Gemini AI and vector search."""

    def __init__(self, preload: bool = False):
        vector_db.initialize_index()
        if preload:
            self.load_documents_to_vector_db()

    def load_documents_to_vector_db(self):
        """Load all active documents from DB into vector store (skip existing)."""
        documents = Document.objects.filter(is_active=True).only(
            "id", "title", "content", "type", "category", "tags"
        )
        vector_docs = []

        for doc in documents:
            doc_id = f"doc_{doc.id}"
            if not vector_db.document_exists(doc_id):
                vector_docs.append({
                    "id": doc_id,
                    "title": doc.title,
                    "content": doc.content,
                    "type": getattr(doc, "type", "Unknown"),
                    "category": getattr(doc, "category", None),
                    "tags": getattr(doc, "tags", None),
                    "source": "database",
                })

        if vector_docs:
            vector_db.add_documents(vector_docs)
            logger.info("Added %s new documents to vector DB", len(vector_docs))

    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        if not query.strip():
            return []
        return vector_db.search(query, top_k)

    def build_gemini_optimized_context(self, documents: List[Dict]) -> str:
        if not documents:
            return "No relevant documents found in the knowledge base."
        parts = ["KNOWLEDGE BASE CONTEXT:"]
        for i, result in enumerate(documents, 1):
            doc = result["document"]
            parts.append(f"\n--- Document {i}: {doc.get('title', 'No title')} ---")
            if doc.get("type"):
                parts.append(f"Type: {doc.get('type')}")
            if doc.get("category"):
                parts.append(f"Category: {doc.get('category')}")
            parts.append(f"Content: {doc.get('content', '')}")
        parts.append("\nInstructions: Use only the provided context. If unsure, say you don't know.")
        return "\n".join(parts)

    def get_conversation_history(self, session_id: int, limit: int = 5) -> List[Dict]:
        from .models import ChatMessage
        messages = (
            ChatMessage.objects.filter(session_id=session_id)
            .only("role", "content")
            .order_by("-created_at")[:limit]
        )
        return [{"role": m.role, "content": m.content} for m in reversed(messages)]

    def process_query(self, query: str, session_id: int = None) -> Dict:
        start_time = time.time()

        # Retrieval
        relevant = self.retrieve_relevant_documents(query)

        # Context
        context = self.build_gemini_optimized_context(relevant)

        # History
        history = self.get_conversation_history(session_id) if session_id else []

        # Generation
        try:
            response = ai_service.generate_response(query, context, history)
        except Exception as e:
            logger.error("AI generation failed: %s", e, exc_info=True)
            response = "Sorry, I couldn’t generate a response this time."

        latency = time.time() - start_time
        return {
            "response": response,
            "relevant_documents": [r["document"] for r in relevant],
            "latency": round(latency, 3),
            "documents_count": len(relevant),
            "context_used": context[:500] + "..." if len(context) > 500 else context,
            "success": True,
        }


rag_service = AdvancedRAGService()
