from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
import uuid
from datetime import datetime
import os

def generate_outgoing_number():
    year = datetime.now().year
    short_id = str(uuid.uuid4().int)[:6]
    return f"{year}-{short_id}"

def attach_logo(email):
    logo_path = os.path.join(
        settings.BASE_DIR,
        "media",
        "logo",
        "og-varna.png"
    )

    with open(logo_path, "rb") as f:
        logo = MIMEImage(f.read())
        logo.add_header("Content-ID", "<logo_image>")
        logo.add_header("Content-Disposition", "inline", filename="logo.png")
        email.attach(logo)


def send_verification_email(user):
    subject = "Потвърдете вашия имейл – Община Варна"

    context = {
        "user": user,
        "code": user.email_verification_code,
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
    }

    html_content = render_to_string("emails/verification_email.html", context)

    text_content = f"""
Здравейте {user.full_name},

Вашият код за потвърждение е: {user.email_verification_code}

Кодът е валиден 10 минути.
"""

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")

    attach_logo(email)  # ← ТУК вграждаме логото

    email.send()


def send_password_reset_email(user):
    subject = "Смяна на парола – Община Варна"

    context = {
        "user": user,
        "code": user.email_verification_code,
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
    }

    html_content = render_to_string("emails/password_reset_email.html", context)

    text_content = f"""
Здравейте {user.full_name},

Вашият код за смяна на парола е: {user.email_verification_code}

Кодът е валиден 10 минути.
"""

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")

    attach_logo(email)  # ← Вграждаме логото

    email.send()

def send_reactivation_email(user):
    subject = "Реактивация на профил – Община Варна"

    context = {
        "user": user,
        "code": user.email_verification_code,
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
    }

    html_content = render_to_string(
        "emails/reactivation_email.html",
        context
    )

    text_content = f"""
Здравейте {user.full_name},

Вашият код за реактивация е: {user.email_verification_code}

Кодът е валиден 10 минути.
"""

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")

    attach_logo(email)

    email.send()

def send_password_changed_email(user):
    subject = "Паролата ви беше променена – Община Варна"

    context = {
        "user": user,
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
    }

    html_content = render_to_string(
        "emails/password_changed_email.html",
        context
    )

    text_content = f"""
Здравейте {user.full_name},

Вашата парола беше успешно променена.

Ако не сте извършили тази промяна, сменете паролата си незабавно.
"""

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")
    attach_logo(email)
    email.send()