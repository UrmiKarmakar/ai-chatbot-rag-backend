from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from core.scheduler import scheduler


def _send_verification_email(user_id: int, email: str):
    """
    Internal function that actually sends the email.
    This is scheduled to run in the background by APScheduler.
    """
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
        fail_silently=True,  # avoid crashing if email backend isn't configured
    )


def schedule_signup_verification_email(user_id: int, email: str):
    """
    Schedule a one-off job to send a verification/welcome email
    shortly after signup.
    """
    run_at = datetime.utcnow() + timedelta(seconds=10)  # delay by 10s
    job_id = f"welcome_email_{user_id}_{int(run_at.timestamp())}"

    scheduler.add_job(
        _send_verification_email,
        "date",
        run_date=run_at,
        args=[user_id, email],
        id=job_id,
        replace_existing=False,
    )
