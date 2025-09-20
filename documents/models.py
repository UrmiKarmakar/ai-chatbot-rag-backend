from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    doc_type = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
