import logging
from django.conf import settings

logger = logging.getLogger(__name__)

if getattr(settings, "SCHEDULER_ENABLED", True):
    try:
        from core.scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        logger.warning("Scheduler could not be started: %s", e)
