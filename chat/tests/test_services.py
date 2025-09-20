import pytest
from chat.services import AdvancedRAGService

@pytest.mark.django_db
def test_process_query_returns_response(monkeypatch):
    service = AdvancedRAGService(preload=False)

    # Mock dependencies only
    monkeypatch.setattr(service, "retrieve_relevant_documents", lambda q, top_k=3: [
        {"document": {"id": "doc_1", "title": "Shipping Policy", "content": "Ships in 5 days"}}
    ])
    monkeypatch.setattr(service, "build_gemini_optimized_context", lambda docs: "Context here")
    monkeypatch.setattr(service, "get_conversation_history", lambda sid, limit=5: [])

    # Now test the real process_query
    result = service.process_query("What is shipping?")
    assert isinstance(result, dict)
    assert "response" in result
    assert result["success"] is True
