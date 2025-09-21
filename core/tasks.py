# core/tasks.py
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_verification_email(user):
    """
    Sends a verification email to a newly registered user.
    This should be scheduled as a background job after signup.
    """
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
