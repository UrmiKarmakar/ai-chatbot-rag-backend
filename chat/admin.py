# chat/admin.py
from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for ChatSession.
    Shows basic session info and allows searching by user.
    """
    list_display = ("id", "user", "title", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "title")
    ordering = ("-created_at",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ChatMessage.
    Shows message role, session, and creation time.
    """
    list_display = ("id", "session", "role", "short_content", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "session__title", "session__user__username")
    ordering = ("created_at",)

    def short_content(self, obj):
        """Preview of the message content."""
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"
