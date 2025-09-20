from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthProfileTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@gmail.com",
            password="1234test"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_authenticated_profile_access(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "testuser@gmail.com")
        self.assertEqual(response.data["username"], "testuser")
