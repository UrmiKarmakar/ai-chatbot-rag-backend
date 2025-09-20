from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "category", "is_active")  # removed created_at
    search_fields = ("title", "content", "tags")
    list_filter = ("type", "category", "is_active")

