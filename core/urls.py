# core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Authentication (signup, login, profile, password reset, etc.)
    path("api/auth/", include("users.urls")),

    # JWT token refresh
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Chat endpoints
    path("api/chat/", include("chat.urls")),

    # Document management endpoints
    path("api/documents/", include("documents.urls")),

    # DRF browsable API login/logout (useful in dev)
    path("api-auth/", include("rest_framework.urls")),
]
