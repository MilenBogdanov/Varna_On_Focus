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

def _send_styled_notification_email(subject, template_name, context, text_content, recipient_list):
    if not recipient_list:
        return

    html_content = render_to_string(template_name, context)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
    )
    email.attach_alternative(html_content, "text/html")
    attach_logo(email)
    email.send(fail_silently=True)


def send_new_signal_email(signal, created_by_email, recipient_list):
    subject = f"Нов сигнал #{signal.id}: {signal.title}"
    context = {
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
        "signal": signal,
        "created_by_email": created_by_email,
    }
    text_content = (
        f"Създаден е нов сигнал от {created_by_email}.\n"
        f"Заглавие: {signal.title}\n"
        f"Адрес: {signal.address}\n"
        f"Описание:\n{signal.description}"
    )
    _send_styled_notification_email(subject, "emails/new_signal_email.html", context, text_content, recipient_list)


def send_new_signal_comment_email(signal, comment, actor_email, recipient_list, actor_type_label):
    subject = f"Нов коментар по сигнал #{signal.id}"
    context = {
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
        "signal": signal,
        "comment": comment,
        "actor_email": actor_email,
        "actor_type_label": actor_type_label,
    }
    text_content = (
        f"{actor_type_label} добави нов коментар към сигнал '{signal.title}'.\n"
        f"Потребител: {actor_email}\n\n"
        f"Коментар:\n{comment.content}"
    )
    _send_styled_notification_email(subject, "emails/new_signal_comment_email.html", context, text_content, recipient_list)


def send_signal_status_changed_email(signal, old_status_display, new_status_display, recipient_list):
    subject = f"Промяна на статус за сигнал #{signal.id}"
    context = {
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
        "signal": signal,
        "old_status_display": old_status_display,
        "new_status_display": new_status_display,
    }
    text_content = (
        f"Статусът на сигнал '{signal.title}' е променен.\n"
        f"Стар статус: {old_status_display}\n"
        f"Нов статус: {new_status_display}"
    )
    _send_styled_notification_email(subject, "emails/signal_status_changed_email.html", context, text_content, recipient_list)


def send_new_news_email(news, recipient_list):
    subject = f"Нова новина: {news.title}"
    context = {
        "title": subject,
        "outgoing_number": generate_outgoing_number(),
        "news": news,
    }
    text_content = (
        f"Заглавие: {news.title}\n"
        f"Тип: {news.get_source_type_display()}\n\n"
        f"{news.content}"
    )
    _send_styled_notification_email(subject, "emails/new_news_email.html", context, text_content, recipient_list)