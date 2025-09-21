# documents/serializers.py
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Document model.
    Matches the fields defined in models.py exactly.
    """

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "file",
            "doc_type",
            "category",
            "tags",
            "is_active",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at", "updated_at"]

    # Field-level validations
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value

    def validate_doc_type(self, value):
        allowed = ["FAQ", "Policy", "Guide", "Other"]
        if value and value not in allowed:
            raise serializers.ValidationError(f"doc_type must be one of {allowed}.")
        return value
