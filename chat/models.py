from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """
    Represents a chat session between a user and the chatbot.
    Each session can contain multiple messages.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Auto-generated from the first user message"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title or 'Untitled'} - {self.created_at:%Y-%m-%d %H:%M}"


class ChatMessage(models.Model):
    """
    Represents a single message in a chat session.
    Can be from user, assistant, or system.
    """
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["session", "created_at"]),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        """
        Ensure the session gets a title from the first user message.
        Only set once, on the first user message.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if (
            is_new
            and self.role == "user"
            and not self.session.title
        ):
            self.session.title = (
                self.content[:50] + "..." if len(self.content) > 50 else self.content
            )
            self.session.save(update_fields=["title"])
