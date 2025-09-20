from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"

    def ready(self):
        from chat.vector_store import vector_db
        try:
            vector_db.initialize_index()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Vector store init skipped: %s", e)
