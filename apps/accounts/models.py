from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import random


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роля'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name

    def get_display_name(self):
        translations = {
            "CITIZEN": "Гражданин",
            "MUNICIPAL_ADMIN": "Общински администратор",
            "SUPER_ADMIN": "Супер администратор",
        }
        return translations.get(self.name, self.name)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # При регистрация по подразбиране НЕ е verified
        user.is_email_verified = False

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        from .models import Role

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)

        role, created = Role.objects.get_or_create(
            name='ADMIN',
            defaults={'description': 'System administrator'}
        )

        extra_fields.setdefault('role', role)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    # -------------------------
    # Основни полета
    # -------------------------
    email = models.EmailField(unique=True, verbose_name='Имейл')
    full_name = models.CharField(max_length=150, verbose_name='Име')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name='Роля'
    )

    # -------------------------
    # Email verification
    # -------------------------
    is_email_verified = models.BooleanField(default=False)

    email_verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    verification_code_expires = models.DateTimeField(
        blank=True,
        null=True
    )

    # -------------------------
    # System fields
    # -------------------------
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Администратор')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създаден на'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Потребител'
        verbose_name_plural = 'Потребители'

    def __str__(self):
        return self.email

    # -------------------------
    # Генериране на код
    # -------------------------
    def generate_verification_code(self):
        code = str(random.randint(100000, 999999))

        self.email_verification_code = code
        self.verification_code_expires = timezone.now() + timedelta(minutes=10)

        self.save()

        return code