# documents/admin.py
from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Document model.
    Provides quick visibility into document metadata and status.
    """
    list_display = ("id", "title", "doc_type", "category", "is_active", "updated_at")
    list_filter = ("doc_type", "is_active", "category", "updated_at")
    search_fields = ("title", "content", "category", "tags")
    ordering = ("-updated_at",)

    def short_content(self, obj):
        """Preview of the document content (first 75 chars)."""
        return (obj.content[:75] + "...") if obj.content and len(obj.content) > 75 else obj.content
    short_content.short_description = "Preview"
