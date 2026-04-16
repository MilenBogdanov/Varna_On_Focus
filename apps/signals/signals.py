import json
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict

from .models import Signal
from apps.audit.models import SignalAudit
from apps.audit.context import get_current_user
from apps.core.choices import AuditOperationType


# 🔹 Запазваме старото състояние временно
@receiver(pre_save, sender=Signal)
def cache_old_signal_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_instance = None
        return

    try:
        old_instance = Signal.objects.get(pk=instance.pk)
        instance._old_instance = old_instance
    except Signal.DoesNotExist:
        instance._old_instance = None


# 🔹 CREATE + UPDATE
@receiver(post_save, sender=Signal)
def create_or_update_signal_audit(sender, instance, created, **kwargs):

    if created:
        SignalAudit.objects.create(
            signal_id=instance.id,
            operation_type=AuditOperationType.CREATE,
            old_data=None,
            new_data=_serialize_signal(instance),
            created_at=instance.created_at,
            performed_by=get_current_user(),
        )
        return

    old_instance = getattr(instance, "_old_instance", None)

    if not old_instance:
        return

    old_data = _serialize_signal(old_instance)
    new_data = _serialize_signal(instance)

    diff_old = {}
    diff_new = {}

    for field in old_data.keys():
        if old_data[field] != new_data[field]:
            diff_old[field] = old_data[field]
            diff_new[field] = new_data[field]

    if diff_old:  # само ако има реални промени
        SignalAudit.objects.create(
            signal_id=instance.id,
            operation_type=AuditOperationType.UPDATE,
            old_data=diff_old,
            new_data=diff_new,
            created_at=instance.updated_at,
            performed_by=get_current_user(),
        )


# 🔹 DELETE
@receiver(post_delete, sender=Signal)
def delete_signal_audit(sender, instance, **kwargs):
    SignalAudit.objects.create(
        signal_id=instance.id,
        operation_type=AuditOperationType.DELETE,
        old_data=_serialize_signal(instance),
        new_data=None,
        created_at=instance.updated_at,
        performed_by=get_current_user(),
    )


# 🔹 Helper за сериализация
def _serialize_signal(instance):
    data = model_to_dict(
        instance,
        fields=[
            "title",
            "description",
            "category",
            "latitude",
            "longitude",
            "address",
            "status",
        ]
    )

    # FK → записваме ID
    data["category"] = instance.category_id

    # Decimal → float
    data["latitude"] = float(instance.latitude)
    data["longitude"] = float(instance.longitude)

    return data
