from django.db import models
from django.conf import settings
from apps.core.choices import SignalStatus
import os
from uuid import uuid4
from PIL import Image
from django.core.exceptions import ValidationError

def signal_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid4()}.{ext}'
    return os.path.join('signals', str(instance.signal_id), filename)

def validate_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("Максималният размер на снимка е 5MB.")

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Signal(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заглавие')
    description = models.TextField(verbose_name='Описание')

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='signals',
        verbose_name='Категория'
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
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес'
    )

    status = models.CharField(
        max_length=20,
        choices=SignalStatus.choices,
        default=SignalStatus.OPEN,
        verbose_name='Статус'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='signals',
        verbose_name='Подаден от'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създаден на'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Последна промяна'
    )

    class Meta:
        db_table = 'signals'
        verbose_name = 'Сигнал'
        verbose_name_plural = 'Сигнали'

    def __str__(self):
        return self.title

class SignalImage(models.Model):
    signal = models.ForeignKey(
        Signal,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Сигнал'
    )

    image = models.ImageField(
        upload_to=signal_image_upload_path,
        validators=[validate_image_size],
        verbose_name='Снимка'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Качена на'
    )

    class Meta:
        db_table = 'signal_images'
        verbose_name = 'Снимка към сигнал'
        verbose_name_plural = 'Снимки към сигнали'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 ENTERPRISE COMPRESSION
        img = Image.open(self.image.path)

        max_width = 1600
        max_height = 1600

        if img.height > max_height or img.width > max_width:
            img.thumbnail((max_width, max_height))

        img.save(self.image.path, quality=80, optimize=True)

    def __str__(self):
        return f'Снимка към сигнал #{self.signal_id}'

class Comment(models.Model):
    signal = models.ForeignKey(
        Signal,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Сигнал'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Потребител'
    )

    content = models.TextField(
        verbose_name='Коментар'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създаден на'
    )

    class Meta:
        db_table = 'comments'
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментари'

    def __str__(self):
        return f'Коментар #{self.id} към сигнал #{self.signal_id}'