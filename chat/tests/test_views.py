import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from chat.models import ChatSession, ChatMessage


@pytest.mark.django_db
def test_chat_view_creates_session_and_messages():
    client = APIClient()
    user = User.objects.create_user(username="urmi", email="urmi@example.com", password="pass12345")
    client.force_authenticate(user=user)

    url = reverse("chat")
    response = client.post(url, {"message": "What is your shipping policy?"}, format="json")

    assert response.status_code == 200
    data = response.json()
    assert "session" in data
    assert "user_message" in data
    assert "assistant_message" in data

    session = ChatSession.objects.get(id=data["session"]["id"])
    assert session.messages.count() == 2  # user + assistant


@pytest.mark.django_db
def test_chat_history_view_returns_sessions():
    client = APIClient()
    user = User.objects.create_user(username="urmi", email="urmi@example.com", password="pass12345")
    client.force_authenticate(user=user)

    session = ChatSession.objects.create(user=user, title="Test Session")
    ChatMessage.objects.create(session=session, role="user", content="Hello")

    url = reverse("chat-history")
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Session"
