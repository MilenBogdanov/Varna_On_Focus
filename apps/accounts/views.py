from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from notifications.services import send_password_changed_email
from .forms import RegisterForm
from .models import User
from notifications.services import (
    send_verification_email,
    send_password_reset_email, send_reactivation_email,
)
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from apps.signals.models import Signal

#--------------
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm

# -------------------------
# REGISTER
# -------------------------

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            user.generate_verification_code()
            send_verification_email(user)

            request.session['verify_email'] = user.email
            return redirect('verify_email')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# -------------------------
# VERIFY EMAIL
# -------------------------

def verify_email(request):
    email = request.session.get('verify_email')

    if not email:
        return redirect('login')

    if request.method == 'POST':
        code = request.POST.get('code')

        try:
            user = User.objects.get(email=email)

            if user.email_verification_code == code:
                if user.verification_code_expires > timezone.now():
                    user.is_email_verified = True
                    user.email_verification_code = None
                    user.verification_code_expires = None
                    user.save()

                    messages.success(request, "Имейлът беше успешно потвърден.")
                    request.session.pop("verify_email", None)
                    return redirect('login')
                else:
                    messages.error(request, "Кодът е изтекъл.")
            else:
                messages.error(request, "Невалиден код.")

        except User.DoesNotExist:
            return redirect('login')

    return render(request, 'accounts/verify_email.html')


# -------------------------
# RESEND CODE
# -------------------------

def resend_code(request):
    email = request.session.get("verify_email")

    if not email:
        return redirect("login")

    try:
        user = User.objects.get(email=email)
        user.generate_verification_code()
        send_verification_email(user)
        messages.success(request, "Нов код беше изпратен.")
    except User.DoesNotExist:
        pass

    return redirect("verify_email")


# -------------------------
# CUSTOM LOGIN
# -------------------------

def banned_account(request):
    return render(request, "accounts/banned_account.html")

def custom_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Невалиден имейл или парола.")
            return render(request, "accounts/login.html")

        # 🔒 Първо проверяваме паролата
        if not user.check_password(password):
            messages.error(request, "Невалиден имейл или парола.")
            return render(request, "accounts/login.html")
        # 🔒 Ако е деактивиран
        if user.is_banned:
            return redirect("banned_account")

        # 🔒 Ако е деактивиран
        if not user.is_active:
            user.generate_verification_code()
            send_reactivation_email(user)

            request.session["reactivate_email"] = user.email
            messages.error(
                request,
                "Профилът е деактивиран. Изпратихме код за реактивация."
            )
            return redirect("reactivate_account")

        # 📧 Ако не е verified
        if not user.is_email_verified:
            request.session['verify_email'] = user.email
            messages.error(request, "Трябва първо да потвърдите имейла си.")
            return redirect("verify_email")

        # ✅ Всичко е ок
        login(request, user)

        return redirect("map")

    return render(request, "accounts/login.html")


# -------------------------
# FORGOT PASSWORD
# -------------------------

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            user.generate_verification_code()
            send_password_reset_email(user)

            request.session['reset_email'] = user.email
            messages.success(request, "Изпратихме код за смяна на парола.")
            return redirect("reset_password")

        except User.DoesNotExist:
            messages.error(request, "Няма потребител с такъв имейл.")

    return render(request, "accounts/forgot_password.html")


# -------------------------
# RESET PASSWORD
# -------------------------

def reset_password(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("login")

    if request.method == "POST":
        code = request.POST.get("code")
        new_password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if new_password != password_confirm:
            messages.error(request, "Паролите не съвпадат.")
            return render(request, "accounts/reset_password.html")

        try:
            user = User.objects.get(email=email)

            if user.email_verification_code == code:
                if user.verification_code_expires > timezone.now():
                    user.password = make_password(new_password)
                    user.email_verification_code = None
                    user.verification_code_expires = None
                    user.save()

                    messages.success(
                        request,
                        "Паролата беше успешно променена.",
                        extra_tags="profile"
                    )
                    request.session.pop("reset_email", None)
                    return redirect("login")
                else:
                    messages.error(request, "Кодът е изтекъл.")
            else:
                messages.error(request, "Невалиден код.")

        except User.DoesNotExist:
            return redirect("login")

    return render(request, "accounts/reset_password.html")

def resend_reset_code(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("login")

    try:
        user = User.objects.get(email=email)
        user.generate_verification_code()
        send_password_reset_email(user)
        messages.success(request, "Нов код за смяна на парола беше изпратен.")
    except User.DoesNotExist:
        pass

    return redirect("reset_password")

@login_required
def profile_view(request):
    user = request.user

    # =============================
    # INITIALS (Teams style)
    # =============================
    if user.full_name:
        parts = user.full_name.strip().split()
        if len(parts) >= 2:
            initials = (parts[0][0] + parts[1][0]).upper()
        else:
            initials = user.full_name[:2].upper()
    else:
        initials = user.email[0].upper()

    # =============================
    # MY SIGNALS (ALL)
    # =============================
    my_signals = Signal.objects.filter(user=user).order_by("-created_at")

    my_stats = my_signals.aggregate(
        total=Count('id'),
        open=Count('id', filter=Q(status="OPEN")),
        in_progress=Count('id', filter=Q(status="IN_PROGRESS")),
        resolved=Count('id', filter=Q(status="RESOLVED")),
        rejected=Count('id', filter=Q(status="REJECTED")),
    )

    # =============================
    # RESOLUTION RATE (НОВО)
    # =============================
    resolution_rate = 0
    if my_stats["total"] and my_stats["total"] > 0:
        resolution_rate = round(
            (my_stats["resolved"] / my_stats["total"]) * 100
        )

    # =============================
    # GLOBAL SIGNALS
    # =============================
    all_signals = Signal.objects.all()

    global_stats = all_signals.aggregate(
        total=Count('id'),
        open=Count('id', filter=Q(status="OPEN")),
        in_progress=Count('id', filter=Q(status="IN_PROGRESS")),
        resolved=Count('id', filter=Q(status="RESOLVED")),
        rejected=Count('id', filter=Q(status="REJECTED")),
    )

    context = {
        "initials": initials,
        "my_stats": my_stats,
        "global_stats": global_stats,
        "resolution_rate": resolution_rate,
        "all_my_signals": my_signals,
        "recent_signals": my_signals[:5],
    }

    return render(request, "accounts/profile.html", context)

@login_required
def delete_account_view(request):
    return render(request, "accounts/delete_account_confirm.html")

@login_required
def confirm_delete_account_view(request):
    if request.method == "POST":
        user = request.user

        user.is_active = False
        user.email_verification_code = None
        user.verification_code_expires = None
        user.save()

        logout(request)

        messages.success(request, "Профилът беше успешно деактивиран.")
        return redirect("map")

    return redirect("profile")

@login_required
def custom_password_change_view(request):

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            # keep logged in
            update_session_auth_hash(request, user)

            send_password_changed_email(user)

            messages.success(
                request,
                "Паролата беше успешно променена.",
                extra_tags="profile"
            )
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {
        "form": form
    })

def reactivate_account(request):
    email = request.session.get("reactivate_email")

    if not email:
        return redirect("login")

    if request.method == "POST":
        code = request.POST.get("code")

        try:
            user = User.objects.get(email=email)

            if user.email_verification_code == code:
                if user.verification_code_expires > timezone.now():
                    user.is_active = True
                    user.email_verification_code = None
                    user.verification_code_expires = None
                    user.save()

                    messages.success(request, "Профилът беше успешно реактивиран.")
                    request.session.pop("reactivate_email", None)

                    login(request, user)
                    return redirect("map")
                else:
                    messages.error(request, "Кодът е изтекъл.")
            else:
                messages.error(request, "Невалиден код.")

        except User.DoesNotExist:
            return redirect("login")

    return render(request, "accounts/reactivate_account.html")

@login_required
def edit_full_name(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")

        if full_name:
            request.user.full_name = full_name
            request.user.save()

            messages.success(
                request,
                "Името беше успешно променено.",
                extra_tags="profile"
            )

    return redirect("profile")