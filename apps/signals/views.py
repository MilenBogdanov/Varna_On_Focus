from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import logout
from datetime import datetime, timedelta

from apps.accounts.decorators import (
    citizen_required,
    municipal_admin_required,
    admin_or_superadmin_required,
)
from apps.core.choices import AuditOperationType
from apps.audit.models import SignalAudit
from apps.signals.models import Category

from .models import Signal, Comment, SignalImage
from .forms import SignalForm, SignalManageForm, AdminCommentForm

from municipality_platform import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from apps.core.choices import SignalStatus

# =========================================================
# 🟢 СЪЗДАВАНЕ НА СИГНАЛ (Citizen)
# =========================================================

@login_required
@citizen_required
def create_signal(request):

    if request.method == "POST":
        form = SignalForm(request.POST, request.FILES)

        if form.is_valid():

            signal = form.save(commit=False)
            signal.user = request.user
            signal.save()

            images = request.FILES.getlist("images")

            MAX_IMAGES = 5
            MAX_SIZE_MB = 5

            if len(images) > MAX_IMAGES:
                signal.delete()
                messages.error(request, f"Можете да качите максимум {MAX_IMAGES} снимки.", extra_tags="signals")
                return redirect("signals:create_signal")

            for image in images:

                if image.size > MAX_SIZE_MB * 1024 * 1024:
                    signal.delete()
                    messages.error(
                        request,
                        "Всяка снимка трябва да е до 5MB.",
                        extra_tags="signals"
                    )
                    return redirect("signals:create_signal")

                try:
                    img = Image.open(image)
                    img = img.convert("RGB")

                    output = BytesIO()
                    img.save(output, format="JPEG", quality=75, optimize=True)
                    output.seek(0)

                    compressed_image = ContentFile(
                        output.read(),
                        name=image.name
                    )

                    SignalImage.objects.create(
                        signal=signal,
                        image=compressed_image
                    )

                except Exception:
                    signal.delete()
                    messages.error(
                        request,
                        "Невалиден формат на изображение.",
                        extra_tags="signals"
                    )
                    return redirect("signals:create_signal")

            # ✅ УСПЕХ
            messages.success(
                request,
                "Сигналът беше успешно създаден.",
                extra_tags="signals"
            )
            return redirect("signals:create_signal")

    else:
        form = SignalForm()

    return render(request, "signals/create_signal.html", {
        "form": form,
    })

# =========================================================
# 🔵 УПРАВЛЕНИЕ НА СИГНАЛ (Municipal Admin)
# =========================================================

@login_required
@admin_or_superadmin_required
def manage_signal(request, signal_id):

    signal = get_object_or_404(Signal, id=signal_id)

    # форма за статус
    status_form = SignalManageForm(instance=signal)

    if request.method == "POST":

        status_form = SignalManageForm(request.POST, instance=signal)

        if status_form.is_valid():

            old_status = signal.status
            updated_signal = status_form.save()

            # Audit само ако статусът се е променил
            if old_status != updated_signal.status:
                SignalAudit.objects.create(
                    signal_id=signal.id,
                    operation_type=AuditOperationType.UPDATE,
                    old_data={"status": old_status},
                    new_data={"status": updated_signal.status},
                    created_at=timezone.now()
                )

            messages.success(
                request,
                "Статусът беше обновен.",
                extra_tags="signals"
            )

            return redirect("signals:manage_signal", signal_id=signal.id)

    # ===============================
    # AUDIT LOG
    # ===============================

    audit_logs = None

    if request.user.is_authenticated:
        if request.user.is_superuser or (
            hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name in ["MUNICIPAL_ADMIN", "SUPER_ADMIN"]
        ):
            audit_logs = (
                SignalAudit.objects
                .filter(signal_id=signal.id)
                .order_by("-created_at")
            )

    # ===============================
    # COMMENTS (read-only)
    # ===============================

    comments = (
        Comment.objects
        .filter(signal=signal)
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "signals/manage_signal.html",
        {
            "signal": signal,
            "form": status_form,
            "audit_logs": audit_logs,
            "comments": comments,
        }
    )


# =========================================================
# 🟡 МОИТЕ СИГНАЛИ (Citizen)
# =========================================================

@login_required
def my_signals(request):

    signals = Signal.objects.filter(user=request.user)

    status = request.GET.get("status")
    category = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    ordering = request.GET.get("ordering")

    # ===== BASIC FILTERS =====
    if status:
        signals = signals.filter(status=status)

    if category:
        signals = signals.filter(category_id=category)

    # ===== DATE VALIDATION =====
    date_from_obj = None
    date_to_obj = None

    try:
        if date_from:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")

        if date_to:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            # include whole day
            date_to_obj = date_to_obj + timedelta(days=1) - timedelta(seconds=1)

        # 🔴 VALIDATION CHECK
        if date_from_obj and date_to_obj and date_from_obj > date_to_obj:
            messages.error(
                request,
                "Началната дата не може да бъде след крайната дата.",
                extra_tags="signals"
            )

            # връщаме без да филтрираме по дата
            date_from_obj = None
            date_to_obj = None

    except ValueError:
        messages.error(
            request,
            "Невалиден формат на дата.",
            extra_tags="signals"
        )

    # ===== APPLY DATE FILTER IF VALID =====
    if date_from_obj:
        signals = signals.filter(created_at__gte=date_from_obj)

    if date_to_obj:
        signals = signals.filter(created_at__lte=date_to_obj)

    # ===== ORDERING =====
    if ordering == "oldest":
        signals = signals.order_by("created_at")
    elif ordering == "az":
        signals = signals.order_by("title")
    elif ordering == "za":
        signals = signals.order_by("-title")
    else:
        signals = signals.order_by("-created_at")

    # ===== PAGINATION =====
    paginator = Paginator(signals, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(
        request,
        "signals/my_signals.html",
        {
            "signals": page_obj,
            "page_obj": page_obj,
            "categories": categories,
        }
    )


# =========================================================
# 🟠 РЕДАКЦИЯ НА СИГНАЛ (Citizen - само OPEN)
# =========================================================

@login_required
@citizen_required
def edit_signal(request, pk):
    signal = get_object_or_404(Signal, pk=pk, user=request.user)

    # 🔒 Само OPEN може да се редактира
    if signal.status != "OPEN":
        messages.error(
            request,
            "Само сигнали със статус 'Отворен' могат да бъдат редактирани.",
            extra_tags="signals"
        )
        return redirect("signals:my_signals")

    if request.method == "POST":
        form = SignalForm(request.POST, instance=signal)

        if form.is_valid():
            updated_signal = form.save()

            # =============================
            # 🗑 Изтриване на снимки
            # =============================
            delete_images = request.POST.getlist("delete_images")

            for image_id in delete_images:
                img = SignalImage.objects.filter(
                    id=image_id,
                    signal=signal
                ).first()

                if img:
                    img.image.delete(save=False)
                    img.delete()

            # =============================
            # 📸 Нови снимки
            # =============================
            new_images = request.FILES.getlist("new_images")

            if signal.images.count() + len(new_images) > 5:
                messages.error(
                    request,
                    "Максимум 5 снимки са позволени.",
                    extra_tags="signals"
                )
                return redirect("signals:edit_signal", pk=signal.pk)

            for image in new_images:
                SignalImage.objects.create(
                    signal=signal,
                    image=image
                )

            messages.success(
                request,
                "Сигналът беше успешно обновен.",
                extra_tags="signals"
            )

            form = SignalForm(instance=signal)

            return render(
                request,
                "signals/edit_signal.html",
                {
                    "form": form,
                    "signal": signal,
                    "images": signal.images.all(),
                    "redirect_after_success": True
                }
            )

    else:
        form = SignalForm(instance=signal)

    return render(
        request,
        "signals/edit_signal.html",
        {
            "form": form,
            "signal": signal,
            "images": signal.images.all()
        }
    )

# =========================================================
# 🔴 ИЗТРИВАНЕ НА СИГНАЛ (Citizen - само OPEN)
# =========================================================

@login_required
@citizen_required
def delete_signal(request, pk):
    signal = get_object_or_404(Signal, pk=pk, user=request.user)

    # ✅ Само OPEN може да се трие
    if signal.status != "OPEN":
        messages.error(
            request,
            "Само сигнали със статус 'Отворен' могат да бъдат изтрити.",
            extra_tags="signals"
        )
        return redirect("signals:my_signals")

    if request.method == "POST":

        # Audit запис
        SignalAudit.objects.create(
            signal_id=signal.id,
            operation_type=AuditOperationType.DELETE,
            old_data={
                "title": signal.title,
                "status": signal.status
            },
            new_data=None,
            created_at=timezone.now()
        )

        signal.delete()

        messages.success(
            request,
            "Сигналът беше успешно изтрит.",
            extra_tags="signals"
        )
        return redirect("signals:my_signals")

    return render(
        request,
        "signals/confirm_delete.html",
        {"signal": signal}
    )

def signal_detail(request, pk):
    signal = get_object_or_404(Signal, pk=pk)

    # =========================
    # Добавяне на коментар
    # =========================
    if request.method == "POST" and request.user.is_authenticated:

        content = request.POST.get("content")

        if content:
            Comment.objects.create(
                signal=signal,
                user=request.user,
                content=content
            )

            return redirect(reverse("signals:signal_detail", args=[signal.id]) + "#comments")

    comments = (
        Comment.objects
        .filter(signal=signal)
        .select_related("user")
        .order_by("-created_at")
    )

    # 🔒 По подразбиране НЯМА audit
    audit_logs = None

    # 🔐 Само администратор може да вижда audit
    if request.user.is_authenticated:
        if request.user.is_superuser:
            audit_logs = (
                SignalAudit.objects
                .filter(signal_id=signal.id)
                .order_by("-created_at")
            )
        elif hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["MUNICIPAL_ADMIN", "SUPER_ADMIN"]:
                audit_logs = (
                    SignalAudit.objects
                    .filter(signal_id=signal.id)
                    .order_by("-created_at")
                )

    can_manage = False
    if request.user.is_authenticated:
        if request.user.is_superuser:
            can_manage = True
        elif hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["MUNICIPAL_ADMIN", "SUPER_ADMIN"]:
                can_manage = True

    return render(
        request,
        "signals/signal_detail.html",
        {
            "signal": signal,
            "comments": comments,
            "audit_logs": audit_logs,
            "can_manage": can_manage,
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        }
    )

@login_required
def confirm_delete_account_view(request):
    if request.method == "POST":
        user = request.user

        user.is_active = False
        user.save()

        logout(request)

        messages.success(
            request,
            "Профилът беше успешно деактивиран.",
            extra_tags="profile"
        )
        return redirect("map")

    return redirect("profile")

# =========================================================
# 🟣 ВСИЧКИ СИГНАЛИ (ADMIN PANEL)
# =========================================================

@login_required
@admin_or_superadmin_required
def all_signals_view(request):
    signals = (
        Signal.objects
        .select_related("category", "user")
    )

    # 🔍 Филтри (по желание - basic)
    status = request.GET.get("status")
    category = request.GET.get("category")
    sort = request.GET.get("sort")

    # ===== SORTING =====
    if sort == "newest":
        signals = signals.order_by("-created_at")
    elif sort == "oldest":
        signals = signals.order_by("created_at")
    elif sort == "az":
        signals = signals.order_by("title")
    elif sort == "za":
        signals = signals.order_by("-title")
    else:
        signals = signals.order_by("-created_at")  # default

    if status:
        signals = signals.filter(status=status)

    if category:
        signals = signals.filter(category_id=category)

    paginator = Paginator(signals, 12)
    page = request.GET.get("page")
    signals_page = paginator.get_page(page)

    categories = Category.objects.all()

    return render(
        request,
        "signals/all_signals.html",
        {
            "signals": signals_page,
            "categories": categories,
            "statuses": SignalStatus.choices
        }
    )

@login_required
@admin_or_superadmin_required
def admin_delete_signal(request, pk):

    signal = get_object_or_404(Signal, pk=pk)

    if request.method == "POST":

        SignalAudit.objects.create(
            signal_id=signal.id,
            operation_type=AuditOperationType.DELETE,
            old_data={
                "title": signal.title,
                "status": signal.status
            },
            new_data=None,
            created_at=timezone.now()
        )

        signal.delete()

        messages.success(
            request,
            "Сигналът беше успешно изтрит от администратор.",
            extra_tags="signals"
        )

        return redirect("signals:all_signals")

    return render(
        request,
        "signals/confirm_delete.html",
        {"signal": signal}
    )