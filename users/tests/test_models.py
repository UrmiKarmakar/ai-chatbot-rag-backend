import pytest
from users.models import User

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username="urmi", email="urmi@example.com", password="pass12345")
    assert user.email == "urmi@example.com"
    assert user.check_password("pass12345")
