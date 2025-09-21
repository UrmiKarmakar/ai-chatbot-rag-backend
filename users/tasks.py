# users/tasks.py
import logging
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from core.scheduler import scheduler

logger = logging.getLogger(__name__)


def _send_verification_email(user_id: int, email: str):
    """
    Internal function that actually sends the email.
    This is scheduled to run in the background by APScheduler.
    """
    try:
        subject = "Welcome to the AI Chatbot!"
        message = (
            "Hi there,\n\n"
            "Your account has been created successfully. "
            "You can now log in and start chatting with the AI assistant.\n\n"
            "Thanks,\nThe Chatbot Team"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,  # fail loudly in logs if backend misconfigured
        )
        logger.info("Verification/welcome email sent to user_id=%s, email=%s", user_id, email)
    except Exception as e:
        logger.error("Failed to send verification email to user_id=%s, email=%s: %s", user_id, email, e)


def schedule_signup_verification_email(user_id: int, email: str):
    """
    Schedule a one-off job to send a verification/welcome email
    shortly after signup.
    """
    run_at = timezone.now() + timedelta(seconds=10)  # delay by 10s
    job_id = f"welcome_email_{user_id}_{int(run_at.timestamp())}"

    try:
        scheduler.add_job(
            _send_verification_email,
            "date",
            run_date=run_at,
            args=[user_id, email],
            id=job_id,
            replace_existing=False,
        )
        logger.info("Scheduled verification email job=%s for user_id=%s at %s", job_id, user_id, run_at)
    except Exception as e:
        logger.error("Failed to schedule verification email for user_id=%s: %s", user_id, e)
