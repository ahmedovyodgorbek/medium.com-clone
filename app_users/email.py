from django.core.mail import send_mail

from django.conf import settings


def send_email_confirmation(user):
    code = user.get_confirmation_code()

    subject = "Your Email Confirmation Code"
    message = f"Hello {user.username},\n\nYour confirmation code is: {code}"

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
