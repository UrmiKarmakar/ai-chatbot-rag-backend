# documents/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class DocumentsConfig(AppConfig):
    """
    AppConfig for the documents app.
    Handles initialization logic for document ingestion if needed.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "documents"

    def ready(self):
        """
        Hook for signals or background tasks.
        Currently no signals are defined, so nothing to import.
        """
        logger.info("Documents app ready — no signals module found.")
