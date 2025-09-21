# core/scheduler.py
import logging
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

# Global scheduler instance (shared across project)
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

        deleted_messages, _ = ChatMessage.objects.filter(created_at__lt=cutoff).delete()
        deleted_sessions, _ = ChatSession.objects.filter(messages__isnull=True).delete()

        logger.info(
            "Cleanup job: deleted %s old messages and %s empty sessions",
            deleted_messages,
            deleted_sessions,
        )
    except Exception as e:
        logger.error("Cleanup job failed: %s", e)


def send_verification_email(user):
    """
    Sends a verification email to a newly registered user.
    This should be scheduled as a one-off job after signup.
    """
    from django.core.mail import send_mail

    try:
        subject = "Verify your account"
        # In production, replace with a signed token or JWT for security
        verification_link = f"{settings.FRONTEND_URL}/verify/{user.id}/"
        message = (
            f"Hi {user.username},\n\n"
            f"Please verify your account by clicking the link below:\n{verification_link}\n\n"
            "If you did not sign up, please ignore this email."
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        logger.info("Verification email sent to %s", user.email)
    except Exception as e:
        logger.error("Failed to send verification email to %s: %s", user.email, e)


def start_scheduler():
    """
    Start the APScheduler with all recurring jobs.
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
