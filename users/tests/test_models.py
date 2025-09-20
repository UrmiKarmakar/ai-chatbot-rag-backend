from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="modeltest",
            email="modeltest@gmail.com",
            password="modeltest1234"
        )
        self.assertEqual(user.username, "modeltest")
        self.assertEqual(user.email, "modeltest@gmail.com")
        self.assertTrue(user.check_password("modeltest1234"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="adminuser",
            email="admin@gmail.com",
            password="Admin1234"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
