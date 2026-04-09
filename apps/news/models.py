from django.db import models
from django.conf import settings
from apps.core.choices import NewsSourceType


class News(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Заглавие'
    )

    content = models.TextField(
        verbose_name='Съдържание'
    )

    source_type = models.CharField(
        max_length=20,
        choices=NewsSourceType.choices,
        verbose_name='Тип новина'
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='news',
        verbose_name='Администратор'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създадена на'
    )

    class Meta:
        db_table = 'news'
        verbose_name = 'Новина'
        verbose_name_plural = 'Новини'

    def __str__(self):
        return self.title

class NewsZone(models.Model):
    news = models.OneToOneField(
        News,
        on_delete=models.CASCADE,
        related_name='zone',
        verbose_name='Новина'
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Име на зона'
    )

    class Meta:
        db_table = 'news_zones'
        verbose_name = 'Зона'
        verbose_name_plural = 'Зони'

    def __str__(self):
        return self.name

class ZonePoint(models.Model):
    zone = models.ForeignKey(
        NewsZone,
        on_delete=models.CASCADE,
        related_name='points',
        verbose_name='Зона'
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        verbose_name='Географска ширина'
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        verbose_name='Географска дължина'
    )

    point_order = models.PositiveIntegerField(
        verbose_name='Ред на точката'
    )

    class Meta:
        db_table = 'zone_points'
        verbose_name = 'Точка на зона'
        verbose_name_plural = 'Точки на зона'
        ordering = ['point_order']

    def __str__(self):
        return f'Точка {self.point_order} – зона {self.zone_id}'