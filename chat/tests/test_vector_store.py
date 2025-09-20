import pytest
from chat.vector_store import VectorDB


@pytest.mark.django_db
def test_add_and_search_documents(tmp_path):
    index_path = tmp_path / "faiss.index"
    docstore_path = tmp_path / "docstore.json"

    db = VectorDB(index_path=str(index_path), docstore_path=str(docstore_path))
    db.initialize_index()

    docs = [
        {"id": "doc_1", "title": "Shipping", "content": "Ships in 5 days"},
        {"id": "doc_2", "title": "Refund", "content": "Refund in 10 days"},
    ]
    assert db.add_documents(docs) is True

    results = db.search("shipping", top_k=1)
    assert len(results) == 1
    assert results[0]["document"]["id"] == "doc_1"

    # Reset clears everything
    db.reset()
    assert db.search("shipping") == []
