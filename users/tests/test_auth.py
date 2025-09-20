import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
def test_user_can_signup():
    client = APIClient()
    response = client.post(reverse("signup"), {
        "username": "urmi",
        "email": "urmi@example.com",
        "password": "strongpass123",
        "password_confirm": "strongpass123",
    })
    assert response.status_code == 201
    assert "access" in response.data

@pytest.mark.django_db
def test_user_can_login_with_email():
    user = User.objects.create_user(username="urmi", email="urmi@example.com", password="strongpass123")
    client = APIClient()
    response = client.post(reverse("login"), {
        "email_or_username": "urmi@example.com",
        "password": "strongpass123",
    })
    assert response.status_code == 200
    assert "access" in response.data
