import logging
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))


def cleanup_old_chats():
    """
    Delete chat messages older than CHAT_RETENTION_DAYS (default: 30)
    and remove empty sessions.
    """
    from chat.models import ChatMessage, ChatSession

    try:
        days = getattr(settings, "CHAT_RETENTION_DAYS", 30)
        cutoff = timezone.now() - timedelta(days=days)

        deleted, _ = ChatMessage.objects.filter(created_at__lt=cutoff).delete()
        ChatSession.objects.filter(messages__isnull=True).delete()

        logger.info("Cleanup job: deleted %s old messages", deleted)
    except Exception as e:
        logger.error("Cleanup job failed: %s", e)


def start_scheduler():
    """
    Start the APScheduler with all jobs.
    """
    if scheduler.running:
        return

    # Daily cleanup at 2 AM
    scheduler.add_job(
        cleanup_old_chats,
        "cron",
        hour=2,
        minute=0,
        id="cleanup_old_chats",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("APScheduler started with cleanup job.")


def stop_scheduler():
    """
    Stop the scheduler gracefully.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
