"""
chat/rag.py
Implements the RAG pipeline: retrieve relevant docs + generate AI response.
"""

import logging
from typing import Dict
from .vector_store import vector_db
from .ai_service import ai_service
from .services import AdvancedRAGService

logger = logging.getLogger(__name__)

# You can either use AdvancedRAGService directly,
# or keep rag_pipeline() as a thin wrapper for convenience.
rag_service = AdvancedRAGService(preload=False)


def rag_pipeline(query: str, session_id: int | None = None) -> Dict:
    """
    Full RAG pipeline: retrieve relevant docs + generate AI response.
    
    Args:
        query (str): User's query.
        session_id (int, optional): Chat session ID for history context.
    
    Returns:
        dict: {
            "response": str,
            "relevant_documents": list,
            "latency": float,
            "documents_count": int,
            "context_used": str,
            "success": bool
        }
    """
    if not query.strip():
        return {
            "response": "Please provide a valid query.",
            "relevant_documents": [],
            "latency": 0.0,
            "documents_count": 0,
            "context_used": "",
            "success": False,
        }

    try:
        return rag_service.process_query(query, session_id=session_id)
    except Exception as e:
        logger.exception("RAG pipeline failed for query='%s'", query)
        return {
            "response": "Sorry, I had trouble processing your request.",
            "relevant_documents": [],
            "latency": 0.0,
            "documents_count": 0,
            "context_used": "",
            "success": False,
        }
