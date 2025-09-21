# documents/models.py
from django.db import models
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/", blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    doc_type = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If file uploaded but no content, extract text
        if self.file and not self.content:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext == ".txt":
                self.content = self.file.read().decode("utf-8", errors="ignore")
            elif ext == ".pdf":
                from PyPDF2 import PdfReader
                reader = PdfReader(self.file)
                self.content = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            elif ext in [".docx"]:
                import docx
                doc = docx.Document(self.file)
                self.content = " ".join([p.text for p in doc.paragraphs])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
