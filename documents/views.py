# documents/views.py
from rest_framework import viewsets, permissions, filters
from .models import Document
from .serializers import DocumentSerializer
from chat.ingestion import ingest_document  # import ingestion function


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

    def perform_create(self, serializer):
        """
        Save document and ingest into FAISS for retrieval.
        """
        doc = serializer.save(uploaded_by=self.request.user)
        ingest_document(doc)

    def perform_update(self, serializer):
        """
        Update document and re-ingest into FAISS.
        """
        doc = serializer.save()
        ingest_document(doc)
