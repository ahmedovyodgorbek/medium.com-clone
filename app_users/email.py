import random
from django.core.mail import send_mail

from django.conf import settings
from .models import ConfirmationCodesModel


def generate_unique_code():
    """Generate a unique 6-digit confirmation code"""
    while True:
        code = str(random.randint(100000, 999999))  # 6-digit code
        if not ConfirmationCodesModel.objects.filter(code=code).exists():
            return code


def send_email_confirmation(user):
    code = generate_unique_code()

    ConfirmationCodesModel.objects.create(code=code, user=user)

    subject = "Your Email Confirmation Code"
    message = f"Hello {user.username},\n\nYour confirmation code is: {code}"

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
