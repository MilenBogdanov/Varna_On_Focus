from django.contrib import admin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    verbose_name = 'Роля'
    verbose_name_plural = 'Роли'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'role', 'is_active')
    search_fields = ('email', 'full_name')
    list_filter = ('role', 'is_active')