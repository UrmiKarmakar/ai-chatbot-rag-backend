# chat/services.py
import time
import logging
from typing import List, Dict
from documents.models import Document
from .vector_store import vector_db
from .ai_services import ai_service

logger = logging.getLogger(__name__)


class AdvancedRAGService:
    """Advanced RAG service with Gemini AI and vector search."""

    def __init__(self, preload: bool = False):
        # Index is already initialized in ChatConfig.ready()
        if preload:
            self.load_documents_to_vector_db()

    def load_documents_to_vector_db(self):
        """Load all active documents from DB into vector store (skip existing)."""
        documents = Document.objects.filter(is_active=True).only(
            "id", "title", "content", "doc_type", "category", "tags"
        )
        vector_docs = []

        for doc in documents:
            doc_id = f"doc_{doc.id}"
            if not vector_db.document_exists(doc_id):
                vector_docs.append({
                    "id": doc_id,
                    "title": doc.title,
                    "content": doc.content,
                    "doc_type": getattr(doc, "doc_type", "Unknown"),
                    "category": getattr(doc, "category", None),
                    "tags": getattr(doc, "tags", []),
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
        parts = ["Knowledge Base Context:"]
        for i, result in enumerate(documents, 1):
            doc = result["document"]
            parts.append(f"\nDocument {i}: {doc.get('title', 'No title')}")
            if doc.get("doc_type"):
                parts.append(f"Type: {doc.get('doc_type')}")
            if doc.get("category"):
                parts.append(f"Category: {doc.get('category')}")
            parts.append(f"Content: {doc.get('content', '')}")
        parts.append(
            "\nInstructions: Use only the provided context. "
            "If the answer is not in the context, say you don't know."
        )
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

        relevant = self.retrieve_relevant_documents(query)
        context = self.build_gemini_optimized_context(relevant)
        history = self.get_conversation_history(session_id) if session_id else []

        try:
            response = ai_service.generate_response(query, context, history)
            success = True
        except Exception as e:
            logger.error("AI generation failed: %s", e, exc_info=True)
            response = "Sorry, I couldn’t generate a response this time."
            success = False

        latency = time.time() - start_time
        logger.info("Processed query in %.3fs (success=%s)", latency, success)

        return {
            "response": response,
            "relevant_documents": [r["document"] for r in relevant],
            "latency": round(latency, 3),
            "documents_count": len(relevant),
            "context_used": context[:500] + "..." if len(context) > 500 else context,
            "success": success,
        }


# Singleton instance
rag_service = AdvancedRAGService()
