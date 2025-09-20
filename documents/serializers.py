from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Document model.
    Handles validation and serialization of document fields.
    """

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "type",
            "category",
            "tags",
            "is_active",
            "uploaded_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uploaded_at", "updated_at"]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value
    def validate_type(self, value):
        allowed = ["FAQ", "Policy", "Guide"]
        if value not in allowed:
            raise serializers.ValidationError(f"Type must be one of {allowed}.")
        return value
