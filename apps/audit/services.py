from django.utils import timezone
from django.forms.models import model_to_dict
from .context import get_current_user
from .models import SignalAudit, NewsAudit
from apps.core.choices import AuditOperationType


def log_signal_operation(signal, operation_type, old_instance=None, old_data=None, new_data=None, performed_by=None):
    """
    Централизиран audit запис за Signal.
    """

    if old_data is None:
        old_data = None

        if old_instance:
            old_data = model_to_dict(old_instance)

    if new_data is None and operation_type != AuditOperationType.DELETE:
        new_data = model_to_dict(signal)

    actor = performed_by if performed_by is not None else get_current_user()

    SignalAudit.objects.create(
        signal_id=signal.id,
        operation_type=operation_type,
        old_data=old_data,
        new_data=new_data,
        created_at=timezone.now(),
        performed_by=actor,
    )


def log_news_operation(news, operation_type, old_instance=None, old_data=None, new_data=None, performed_by=None):
    """
    Централизиран audit запис за News.
    """

    if old_data is None:
        old_data = None

        if old_instance:
            old_data = model_to_dict(old_instance)

    if new_data is None and operation_type != AuditOperationType.DELETE:
        new_data = model_to_dict(news)

    actor = performed_by if performed_by is not None else get_current_user()

    NewsAudit.objects.create(
        news_id=news.id,
        operation_type=operation_type,
        old_data=old_data,
        new_data=new_data,
        created_at=timezone.now(),
        performed_by=actor,
    )