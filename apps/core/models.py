from django.db import models


class Zone(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Име на зона'
    )

    coordinates = models.JSONField(
        verbose_name='Координати (polygon)'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създадена на'
    )

    class Meta:
        db_table = 'zones'
        verbose_name = 'Зона'
        verbose_name_plural = 'Зони'

    def __str__(self):
        return self.name
