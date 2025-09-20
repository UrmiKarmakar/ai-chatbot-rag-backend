import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from documents.models import Document


@pytest.mark.django_db
def test_document_model_str():
    doc = Document.objects.create(
        title="Shipping Policy",
        content="All orders ship within 3 business days.",
        type="Policy",
        category="Shipping",
        tags=["delivery", "policy"],
        is_active=True,
    )
    assert str(doc) == "Shipping Policy"


@pytest.mark.django_db
def test_create_document_via_api():
    client = APIClient()
    # Authenticate a dummy user
    from users.models import User
    user = User.objects.create_user(username="urmi", email="urmi@example.com", password="pass12345")
    client.force_authenticate(user=user)

    url = reverse("document-list")  # from DRF router
    payload = {
        "title": "Return Policy",
        "content": "Items can be returned within 30 days.",
        "type": "Policy",
        "category": "Returns",
        "tags": ["returns", "policy"],
        "is_active": True,
    }
    response = client.post(url, payload, format="json")

    assert response.status_code == 201
    assert response.data["title"] == "Return Policy"
    assert Document.objects.count() == 1


@pytest.mark.django_db
def test_list_documents_api_filters_active_only():
    client = APIClient()
    from users.models import User
    user = User.objects.create_user(username="urmi", email="urmi@example.com", password="pass12345")
    client.force_authenticate(user=user)

    Document.objects.create(title="Active Doc", content="Visible", type="Guide", is_active=True)
    Document.objects.create(title="Inactive Doc", content="Hidden", type="Guide", is_active=False)

    url = reverse("document-list")
    response = client.get(url)

    titles = [doc["title"] for doc in response.data]
    assert "Active Doc" in titles
    assert "Inactive Doc" not in titles

    # If ?all=true is passed, both should appear
    response_all = client.get(url + "?all=true")
    titles_all = [doc["title"] for doc in response_all.data]
    assert "Inactive Doc" in titles_all
