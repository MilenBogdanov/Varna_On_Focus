from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from email.mime.image import MIMEImage
import os
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
from apps.audit.models import SignalAudit, NewsAudit
from apps.core.choices import AuditOperationType
import csv
from apps.accounts.decorators import admin_or_superadmin_required, superadmin_required
from apps.accounts.models import User, Role
from apps.signals.models import Signal
from apps.core.choices import SignalStatus
from apps.news.models import News
from apps.core.choices import NewsSourceType



def map_view(request):
    return render(
        request,
        'map.html',
        {
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
    )

@login_required
@admin_or_superadmin_required
def admin_dashboard(request):
    now = timezone.now()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_signals = Signal.objects.count()
    open_signals = Signal.objects.filter(status=SignalStatus.OPEN).count()
    in_progress_signals = Signal.objects.filter(status=SignalStatus.IN_PROGRESS).count()
    resolved_signals = Signal.objects.filter(status=SignalStatus.RESOLVED).count()
    rejected_signals = Signal.objects.filter(status=SignalStatus.REJECTED).count()
    created_today = Signal.objects.filter(created_at__gte=start_today).count()
    total_news = News.objects.count()
    news_today = News.objects.filter(created_at__gte=start_today).count()

    citizens_count = User.objects.filter(role__name="CITIZEN").count()
    municipal_admin_count = User.objects.filter(role__name="MUNICIPAL_ADMIN").count()
    super_admin_count = User.objects.filter(role__name="SUPER_ADMIN").count()

    top_categories = (
        Signal.objects.values("category__id", "category__name")
        .annotate(total=Count("id"))
        .order_by("-total", "category__name")[:6]
    )

    status_breakdown_raw = [
        ("Отворени", open_signals),
        ("В процес", in_progress_signals),
        ("Решени", resolved_signals),
        ("Отхвърлени", rejected_signals),
    ]

    status_breakdown = []
    for label, count in status_breakdown_raw:
        percent = (count / total_signals * 100) if total_signals else 0
        status_breakdown.append(
            {"label": label, "count": count, "percent": round(percent, 1)}
        )

    news_by_type_map = dict(
        News.objects.values_list("source_type")
        .annotate(total=Count("id"))
    )
    news_breakdown = []
    for value, label in NewsSourceType.choices:
        count = news_by_type_map.get(value, 0)
        percent = (count / total_news * 100) if total_news else 0
        news_breakdown.append(
            {"value": value, "label": label, "count": count, "percent": round(percent, 1)}
        )

    timeline = []
    timeline_max = 1
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        signals_count_day = Signal.objects.filter(
            created_at__gte=day_start, created_at__lt=day_end
        ).count()
        news_count_day = News.objects.filter(
            created_at__gte=day_start, created_at__lt=day_end
        ).count()

        timeline_max = max(timeline_max, signals_count_day, news_count_day)
        timeline.append(
            {
                "date": day_start.strftime("%d.%m"),
                "signals": signals_count_day,
                "news": news_count_day,
            }
        )

    for row in timeline:
        row["signals_height"] = int((row["signals"] / timeline_max) * 100) if timeline_max else 0
        row["news_height"] = int((row["news"] / timeline_max) * 100) if timeline_max else 0

    recent_signals = (
        Signal.objects.select_related("category", "user")
        .order_by("-created_at")[:10]
    )

    context = {
        "total_signals": total_signals,
        "open_signals": open_signals,
        "in_progress_signals": in_progress_signals,
        "resolved_signals": resolved_signals,
        "rejected_signals": rejected_signals,
        "created_today": created_today,
        "total_news": total_news,
        "news_today": news_today,
        "citizens_count": citizens_count,
        "municipal_admin_count": municipal_admin_count,
        "super_admin_count": super_admin_count,
        "top_categories": top_categories,
        "status_breakdown": status_breakdown,
        "news_breakdown": news_breakdown,
        "timeline": timeline,
        "recent_signals": recent_signals,
    }
    return render(request, "dashboard/admin_dashboard.html", context)

@login_required
@superadmin_required
def super_admin_panel(request):
    from django.urls import reverse

    now = timezone.now()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_signals = Signal.objects.count()
    open_signals = Signal.objects.filter(status=SignalStatus.OPEN).count()
    in_progress_signals = Signal.objects.filter(status=SignalStatus.IN_PROGRESS).count()
    resolved_signals = Signal.objects.filter(status=SignalStatus.RESOLVED).count()
    created_today = Signal.objects.filter(created_at__gte=start_today).count()

    total_news = News.objects.count()
    news_today = News.objects.filter(created_at__gte=start_today).count()

    citizens_count = User.objects.filter(role__name="CITIZEN").count()
    municipal_admin_count = User.objects.filter(role__name="MUNICIPAL_ADMIN").count()
    super_admin_count = User.objects.filter(role__name="SUPER_ADMIN").count()

    recent_signals = Signal.objects.select_related("category", "user").order_by("-created_at")[:6]

    users_admin_url = reverse("admin:accounts_user_changelist")
    roles_admin_url = reverse("admin:accounts_role_changelist")
    signals_admin_url = reverse("admin:signals_signal_changelist")
    news_admin_url = reverse("admin:news_news_changelist")
    comments_admin_url = reverse("admin:signals_comment_changelist")

    citizen_role = Role.objects.filter(name="CITIZEN").only("id").first()
    municipal_role = Role.objects.filter(name="MUNICIPAL_ADMIN").only("id").first()
    super_role = Role.objects.filter(name="SUPER_ADMIN").only("id").first()

    users_by_role_links = {
        "citizens": f"{users_admin_url}?role__id__exact={citizen_role.id}" if citizen_role else users_admin_url,
        "municipal_admins": f"{users_admin_url}?role__id__exact={municipal_role.id}" if municipal_role else users_admin_url,
        "super_admins": f"{users_admin_url}?role__id__exact={super_role.id}" if super_role else users_admin_url,
    }

    context = {
        "total_signals": total_signals,
        "open_signals": open_signals,
        "in_progress_signals": in_progress_signals,
        "resolved_signals": resolved_signals,
        "created_today": created_today,
        "total_news": total_news,
        "news_today": news_today,
        "citizens_count": citizens_count,
        "municipal_admin_count": municipal_admin_count,
        "super_admin_count": super_admin_count,
        "recent_signals": recent_signals,
        "users_admin_url": users_admin_url,
        "roles_admin_url": roles_admin_url,
        "signals_admin_url": signals_admin_url,
        "news_admin_url": news_admin_url,
        "comments_admin_url": comments_admin_url,
        "users_by_role_links": users_by_role_links,
    }
    return render(request, "dashboard/super_admin_panel.html", context)

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

@login_required
@admin_or_superadmin_required
def audit_panel(request):
    source_filter = request.GET.get("source", "ALL")
    operation_filter = request.GET.get("operation", "ALL")
    actor_filter = request.GET.get("actor", "").strip()
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    signal_logs = SignalAudit.objects.select_related("performed_by").all()
    news_logs = NewsAudit.objects.select_related("performed_by").all()

    if operation_filter != "ALL":
        signal_logs = signal_logs.filter(operation_type=operation_filter)
        news_logs = news_logs.filter(operation_type=operation_filter)

    if actor_filter:
        signal_logs = signal_logs.filter(performed_by__email__icontains=actor_filter)
        news_logs = news_logs.filter(performed_by__email__icontains=actor_filter)

    if date_from:
        signal_logs = signal_logs.filter(created_at__date__gte=date_from)
        news_logs = news_logs.filter(created_at__date__gte=date_from)

    if date_to:
        signal_logs = signal_logs.filter(created_at__date__lte=date_to)
        news_logs = news_logs.filter(created_at__date__lte=date_to)

    entries = []

    if source_filter in ["ALL", "SIGNAL"]:
        entries.extend(
            {
                "source": "Сигнал",
                "entity_id": log.signal_id,
                "operation": log.get_operation_type_display(),
                "operation_raw": log.operation_type,
                "performed_by": log.performed_by.email if log.performed_by else "Система",
                "created_at": log.created_at,
            }
            for log in signal_logs
        )

    if source_filter in ["ALL", "NEWS"]:
        entries.extend(
            {
                "source": "Новина",
                "entity_id": log.news_id,
                "operation": log.get_operation_type_display(),
                "operation_raw": log.operation_type,
                "performed_by": log.performed_by.email if log.performed_by else "Система",
                "created_at": log.created_at,
            }
            for log in news_logs
        )

    entries.sort(key=lambda item: item["created_at"], reverse=True)

    if request.GET.get("export") == "excel":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="audit_panel_export.csv"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow(["Тип", "ID", "Операция", "Извършил", "Дата"])
        for row in entries:
            writer.writerow([
                row["source"],
                row["entity_id"],
                row["operation"],
                row["performed_by"],
                row["created_at"].strftime("%d.%m.%Y %H:%M"),
            ])
        return response

    context = {
        "entries": entries[:300],
        "source_filter": source_filter,
        "operation_filter": operation_filter,
        "actor_filter": actor_filter,
        "date_from": date_from,
        "date_to": date_to,
        "operations": AuditOperationType.choices,
    }
    return render(request, "dashboard/audit_panel.html", context)