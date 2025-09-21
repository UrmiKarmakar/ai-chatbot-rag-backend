# documents/urls.py
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
# Use plural for both the URL prefix and the basename for consistency
router.register(r"documents", DocumentViewSet, basename="documents")

urlpatterns = router.urls
