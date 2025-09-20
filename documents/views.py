from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing knowledge base documents.
    Provides list, create, retrieve, update, and delete actions.
    """
    queryset = Document.objects.all().order_by("-uploaded_at")
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter only active documents unless ?all=true is passed.
        """
        queryset = super().get_queryset()
        show_all = self.request.query_params.get("all")
        if not show_all:
            queryset = queryset.filter(is_active=True)
        return queryset
