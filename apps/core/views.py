from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
import os
from datetime import datetime



def map_view(request):
    return render(
        request,
        'map.html',
        {
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
    )

def contact(request):

    if request.method == "POST":

        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # 🔥 NEW
        category = request.POST.get("category")
        custom_category = request.POST.get("custom_category")

        user = request.user if request.user.is_authenticated else None

        outgoing_number = datetime.now().strftime("%Y%m%d%H%M%S")

        # ---------------- CATEGORY ----------------
        CATEGORY_MAP = {
            "question": "Въпрос",
            "complaint": "Оплакване",
            "suggestion": "Предложение",
        }

        if category == "other" and custom_category:
            category_display = custom_category
        else:
            category_display = CATEGORY_MAP.get(category, "Няма категория")

        # ---------------- ROLE TRANSLATION ----------------
        ROLE_TRANSLATIONS = {
            "CITIZEN": "Гражданин",
            "MUNICIPAL_ADMIN": "Общински служител",
            "SUPER_ADMIN": "Супер администратор"
        }

        # ---------------- USER INFO ----------------
        user_info = f"Имейл (въведен): {email}\n"

        role_display = ""

        if user and hasattr(user, "role"):

            role_code = user.role.name
            role_bg = ROLE_TRANSLATIONS.get(role_code, role_code)

            role_display = f"{role_bg} / {role_code}"

            user_info += (
                f"Потребител: {user.full_name}\n"
                f"Роля: {role_display}\n"
            )

        # ---------------- TEXT VERSION ----------------
        body = f"""
НОВО СЪОБЩЕНИЕ ОТ КОНТАКТ ФОРМА

Категория: {category_display}

{user_info}

Тема: {subject}

Съобщение:
{message}
"""

        # ---------------- HTML VERSION ----------------
        html_content = render_to_string(
            "emails/base_email.html",
            {
                "title": subject,
                "outgoing_number": outgoing_number,

                "custom_content": f"""
                <div style="padding:30px; font-family:Arial, sans-serif; color:#333;">

                    <h3 style="margin-bottom:15px;">
                        Ново съобщение от контакт формата
                    </h3>

                    <p><strong>Категория:</strong> {category_display}</p>
                    <p><strong>Тема:</strong> {subject}</p>
                    <p><strong>Имейл (въведен):</strong> {email}</p>

                    {f'''
                    <p><strong>Потребител:</strong> {user.full_name}</p>
                    <p><strong>Роля:</strong> {role_display}</p>
                    ''' if user else ''}

                    <hr style="margin:20px 0;">

                    <div style="
                        background:#f7fbff;
                        padding:20px;
                        border-radius:12px;
                        border:1px solid #e3f2fd;
                        white-space:pre-line;
                    ">
                        {message}
                    </div>

                </div>
                """
            }
        )

        # ---------------- EMAIL TO MUNICIPALITY ----------------
        msg = EmailMultiAlternatives(
            subject=f"[{category_display}] {subject}",
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.MUNICIPALITY_STAFF_EMAIL],
            reply_to=[email],
        )

        msg.attach_alternative(html_content, "text/html")

        # ---------------- LOGO ----------------
        logo_path = os.path.join(settings.MEDIA_ROOT, "logo/og-varna.png")

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo = MIMEImage(f.read())
                logo.add_header('Content-ID', '<logo_image>')
                msg.attach(logo)

        msg.send()

        # ---------------- AUTO REPLY ----------------
        auto_reply_html = render_to_string(
            "emails/base_email.html",
            {
                "title": "Получихме вашето съобщение",
                "outgoing_number": outgoing_number,
                "custom_content": f"""
                <div style="padding:30px; font-family:Arial, sans-serif; color:#333;">

                    <h3>Вашето съобщение беше получено</h3>

                    <p>Благодарим ви, че се свързахте с Община Варна.</p>

                    <p><strong>Категория:</strong> {category_display}</p>
                    <p><strong>Тема:</strong> {subject}</p>

                    <hr style="margin:20px 0;">

                    <p><strong>Вашето съобщение:</strong></p>

                    <div style="
                        background:#f7fbff;
                        padding:18px;
                        border-radius:12px;
                        border:1px solid #e3f2fd;
                        white-space:pre-line;
                        margin-top:10px;
                    ">
                        {message}
                    </div>

                    <hr style="margin:20px 0;">

                    <p>
                        Ще прегледаме съобщението ви и ще ви изпратим отговор по имейл
                        във възможно най-кратък срок.
                    </p>

                </div>
                """
            }
        )

        auto_msg = EmailMultiAlternatives(
            subject="Получихме вашето съобщение",
            body="Вашето съобщение беше получено.",
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )

        auto_msg.attach_alternative(auto_reply_html, "text/html")

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo = MIMEImage(f.read())
                logo.add_header('Content-ID', '<logo_image>')
                auto_msg.attach(logo)

        auto_msg.send()

        return render(request, "contact/contact.html", {
            "success": True
        })

    return render(request, "contact/contact.html")
