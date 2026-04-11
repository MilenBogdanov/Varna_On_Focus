from django.contrib import admin
from django import forms
from .models import User, Role
from .constants import Roles


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    verbose_name = 'Роля'
    verbose_name_plural = 'Роли'


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        is_staff = cleaned_data.get('is_staff')
        is_superuser = cleaned_data.get('is_superuser')

        super_admin_role = Role.objects.filter(name=Roles.SUPER_ADMIN).first()

        if super_admin_role and (
            role == super_admin_role or is_staff or is_superuser
        ):
            cleaned_data['role'] = super_admin_role
            cleaned_data['is_staff'] = True
            cleaned_data['is_superuser'] = True
        elif super_admin_role and role != super_admin_role:
            cleaned_data['is_staff'] = False
            cleaned_data['is_superuser'] = False

        return cleaned_data


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('id', 'email', 'full_name', 'role', 'is_active', 'is_banned')
    search_fields = ('email', 'full_name')
    list_filter = ('role', 'is_active', 'is_banned')
    fields = (
        'email',
        'full_name',
        'password',
        'role',
        'is_superuser',
        'is_staff',
        'is_active',
        'is_banned',
        'is_email_verified',
        'last_login',
        'created_at',
    )
    readonly_fields = ('password', 'last_login', 'created_at')