from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),  # signup, login, profile
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/chat/", include("chat.urls")),   # chat endpoints
    path("api/documents/", include("documents.urls")),  # optional future
]
