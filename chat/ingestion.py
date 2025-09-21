"""
Handles ingestion of documents into the retrieval system (FAISS).
"""
import logging
from typing import List
from .vector_store import vector_db  # use the singleton instance

logger = logging.getLogger(__name__)


def ingest_document(document) -> bool:
    """
    Ingest a single Document model instance into FAISS.

    Args:
        document (Document): Django Document instance

    Returns:
        bool: True if ingestion succeeded, False otherwise
    """
    if not document or not document.content or not document.content.strip():
        logger.warning("Skipping ingestion: empty or invalid document")
        return False

    # Split content into chunks (simple fixed-size)
    chunks = [document.content[i:i+500] for i in range(0, len(document.content), 500)]

    docs = []
    for idx, chunk in enumerate(chunks, start=1):
        docs.append({
            "id": f"{document.id}_{idx}",
            "title": document.title,
            "doc_type": getattr(document, "doc_type", None),
            "category": getattr(document, "category", None),
            "tags": getattr(document, "tags", []),
            "content": chunk,
            "source": "database",
        })

    success = vector_db.add_documents(docs)

    if success:
        logger.info("Ingested document %s (%d chunks)", document.id, len(chunks))
    else:
        logger.error("Failed to ingest document %s", document.id)

    return success


def ingest_documents_bulk(documents: List) -> bool:
    """
    Ingest multiple Document model instances at once.

    Args:
        documents (List[Document]): List of Document instances

    Returns:
        bool: True if all ingested successfully, False otherwise
    """
    prepared = []
    for doc in documents:
        if not doc.content or not doc.content.strip():
            continue
        chunks = [doc.content[i:i+500] for i in range(0, len(doc.content), 500)]
        for idx, chunk in enumerate(chunks, start=1):
            prepared.append({
                "id": f"{doc.id}_{idx}",
                "title": doc.title,
                "doc_type": getattr(doc, "doc_type", None),
                "category": getattr(doc, "category", None),
                "tags": getattr(doc, "tags", []),
                "content": chunk,
                "source": "database",
            })

    if not prepared:
        logger.warning("No valid documents to ingest")
        return False

    return vector_db.add_documents(prepared)
