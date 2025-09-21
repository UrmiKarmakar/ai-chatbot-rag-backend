# chat/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"

    def ready(self):
        """
        Initialize the vector store when the app is ready.
        Guard against multiple calls (e.g., Django autoreload).
        """
        from .vector_store import vector_db  # local import to avoid circular issues

        if getattr(vector_db, "_initialized", False):
            # Already initialized, skip
            return

        try:
            vector_db.initialize_index()
            vector_db._initialized = True
            logger.info("Vector store initialized successfully on app startup.")
        except Exception as e:
            logger.warning("Vector store initialization skipped in ChatConfig: %s", e)
