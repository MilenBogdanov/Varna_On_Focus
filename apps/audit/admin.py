from django.contrib import admin
from .models import SignalAudit, NewsAudit


class ReadOnlyAdmin(admin.ModelAdmin):
    """
    Общ read-only admin клас за audit таблици
    """

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SignalAudit)
class SignalAuditAdmin(ReadOnlyAdmin):
    list_display = (
        'signal_id',
        'operation_type',
        'created_at',
    )
    list_filter = ('operation_type', 'created_at')
    search_fields = ('signal_id',)


@admin.register(NewsAudit)
class NewsAuditAdmin(ReadOnlyAdmin):
    list_display = (
        'news_id',
        'operation_type',
        'created_at',
    )
    list_filter = ('operation_type', 'created_at')
    search_fields = ('news_id',)
