from django.utils import timezone
from django.forms.models import model_to_dict

from .models import SignalAudit, NewsAudit
from apps.core.choices import AuditOperationType


def log_signal_operation(signal, operation_type, old_instance=None):
    """
    Централизиран audit запис за Signal.
    """

    old_data = None
    new_data = None

    if old_instance:
        old_data = model_to_dict(old_instance)

    if operation_type != AuditOperationType.DELETE:
        new_data = model_to_dict(signal)

    SignalAudit.objects.create(
        signal_id=signal.id,
        operation_type=operation_type,
        old_data=old_data,
        new_data=new_data,
        created_at=timezone.now()
    )


def log_news_operation(news, operation_type, old_instance=None):
    """
    Централизиран audit запис за News.
    """

    old_data = None
    new_data = None

    if old_instance:
        old_data = model_to_dict(old_instance)

    if operation_type != AuditOperationType.DELETE:
        new_data = model_to_dict(news)

    NewsAudit.objects.create(
        news_id=news.id,
        operation_type=operation_type,
        old_data=old_data,
        new_data=new_data,
        created_at=timezone.now()
    )
