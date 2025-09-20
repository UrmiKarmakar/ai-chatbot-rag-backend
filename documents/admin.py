from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "doc_type", "is_active", "updated_at"]
    list_filter = ["doc_type", "is_active", "category"]
    search_fields = ["title", "content", "category", "tags"]
