
"""
SMTP email sending
"""

from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, code):
    send_mail(
        subject="Email Verification",
        message=f"Your verification code is: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )