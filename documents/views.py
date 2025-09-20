from rest_framework import viewsets, permissions, filters
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing knowledge base documents.
    Provides list, create, retrieve, update, and delete actions.
    Supports filtering by active status, category, and tags.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "category", "tags"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """
        Optionally filter only active documents unless ?all=true is passed.
        Supports filtering by category and tags.
        """
        queryset = Document.objects.all()
        show_all = self.request.query_params.get("all")
        category = self.request.query_params.get("category")
        tags = self.request.query_params.getlist("tags")

        if not show_all:
            queryset = queryset.filter(is_active=True)

        if category:
            queryset = queryset.filter(category=category)

        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=tag)

        return queryset
