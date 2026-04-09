from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('login/', views.custom_login, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-reset-code/', views.resend_reset_code, name='resend_reset_code'),
    path("profile/", views.profile_view, name="profile"),
    path("delete-account/", views.delete_account_view, name="delete_account"),
    path("confirm-delete/", views.confirm_delete_account_view, name="confirm_delete_account"),
    path("change-password/", views.custom_password_change_view, name="custom_password_change"),
    path("reactivate/", views.reactivate_account, name="reactivate_account"),
    path("edit-full-name/", views.edit_full_name, name="edit_full_name"),
]