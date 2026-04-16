from django.db import models
from django.conf import settings
from apps.core.choices import AuditOperationType


class SignalAudit(models.Model):
    signal_id = models.IntegerField(verbose_name='ID на сигнал')
    operation_type = models.CharField(
        max_length=10,
        choices=AuditOperationType.choices,
        verbose_name='Тип операция'
    )

    old_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Стари данни'
    )

    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Нови данни'
    )

    created_at = models.DateTimeField(
        verbose_name='Дата'
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signal_audit_entries',
        verbose_name='Променено от'
    )

    class Meta:
        db_table = 'signals_audit'
        verbose_name = 'Лог на сигнал'
        verbose_name_plural = 'Логове на сигнали'

    def __str__(self):
        return f'Лог за сигнал #{self.signal_id}'

class NewsAudit(models.Model):
    news_id = models.IntegerField(verbose_name='ID на новина')
    operation_type = models.CharField(
        max_length=10,
        choices=AuditOperationType.choices,
        verbose_name='Тип операция'
    )

    old_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Стари данни'
    )

    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Нови данни'
    )

    created_at = models.DateTimeField(
        verbose_name='Дата'
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_audit_entries',
        verbose_name='Променено от'
    )

    class Meta:
        db_table = 'news_audit'
        verbose_name = 'Лог на новина'
        verbose_name_plural = 'Логове на новини'

    def __str__(self):
        return f'Лог за новина #{self.news_id}'