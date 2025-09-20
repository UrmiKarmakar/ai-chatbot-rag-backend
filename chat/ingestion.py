"""
Handles ingestion of documents into the retrieval system (FAISS, Pinecone, etc.)
"""
import logging
from typing import Dict, List
from .vector_store import vector_db

logger = logging.getLogger(__name__)


def ingest_document(content: str, metadata: Dict = None) -> bool:
    """
    Ingest a single document into the retrieval system (FAISS).
    
    Args:
        content (str): The raw text of the document.
        metadata (dict): Optional metadata (id, title, type, category, tags, etc.)
    
    Returns:
        bool: True if ingestion succeeded, False otherwise.
    """
    if not content.strip():
        logger.warning("Skipping ingestion: empty content")
        return False

    doc_id = metadata.get("id") if metadata else None
    if not doc_id:
        # Generate a unique ID if not provided
        import uuid
        doc_id = f"doc_{uuid.uuid4().hex}"

    document = {
        "id": doc_id,
        "title": metadata.get("title") if metadata else "Untitled",
        "content": content,
        "type": metadata.get("type") if metadata else None,
        "category": metadata.get("category") if metadata else None,
        "tags": metadata.get("tags") if metadata else [],
        "source": metadata.get("source") if metadata else "manual_ingest",
    }

    success = vector_db.add_documents([document])
    if success:
        logger.info("Ingested document: %s (%s chars)", document["id"], len(content))
    else:
        logger.error("Failed to ingest document: %s", document["id"])
    return success


def ingest_documents_bulk(docs: List[Dict]) -> bool:
    """
    Ingest multiple documents at once.
    
    Args:
        docs (List[Dict]): Each dict should have {"content": str, "metadata": dict}
    
    Returns:
        bool: True if all ingested successfully, False otherwise.
    """
    prepared = []
    for d in docs:
        content = d.get("content", "")
        metadata = d.get("metadata", {})
        if not content.strip():
            continue
        doc_id = metadata.get("id") or f"doc_{len(prepared)}"
        prepared.append({
            "id": doc_id,
            "title": metadata.get("title", "Untitled"),
            "content": content,
            "type": metadata.get("type"),
            "category": metadata.get("category"),
            "tags": metadata.get("tags", []),
            "source": metadata.get("source", "bulk_ingest"),
        })

    if not prepared:
        logger.warning("No valid documents to ingest")
        return False

    return vector_db.add_documents(prepared)
