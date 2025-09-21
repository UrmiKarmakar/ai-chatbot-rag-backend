# chat/rag.py
"""
Implements the RAG pipeline: retrieve relevant docs + generate AI response.
"""

import logging
from typing import Dict, Optional
from .services import AdvancedRAGService

logger = logging.getLogger(__name__)

# Initialize the RAG service (without preloading by default)
rag_service = AdvancedRAGService(preload=False)


def rag_pipeline(query: str, session_id: Optional[int] = None) -> Dict:
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
        logger.exception("RAG pipeline failed for query='%s'", query, exc_info=True)
        return {
            "response": "Sorry, I had trouble processing your request.",
            "relevant_documents": [],
            "latency": 0.0,
            "documents_count": 0,
            "context_used": "",
            "success": False,
        }
