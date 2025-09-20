import pytest
from chat.services import AdvancedRAGService


@pytest.mark.django_db
def test_process_query_returns_response(monkeypatch):
    service = AdvancedRAGService(preload=False)

    # Mock retrieval
    monkeypatch.setattr(service, "retrieve_relevant_documents", lambda q, top_k=3: [
        {"document": {"id": "doc_1", "title": "Shipping Policy", "content": "Ships in 5 days"}}
    ])

    # Mock AI generation
    monkeypatch.setattr(service, "build_gemini_optimized_context", lambda docs: "Context here")
    monkeypatch.setattr(service, "get_conversation_history", lambda sid, limit=5: [])
    monkeypatch.setattr(service, "process_query", lambda q, sid=None: {
        "response": "Mocked response",
        "relevant_documents": [],
        "latency": 0.1,
        "documents_count": 1,
        "context_used": "Context here",
        "success": True,
    })

    result = service.process_query("What is shipping?")
    assert result["response"] == "Mocked response"
    assert result["success"] is True
