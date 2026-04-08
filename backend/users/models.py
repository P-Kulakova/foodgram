from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

EMAIL_MAX_LENGTH = 254


class CustomUserManager(UserManager):
    """Менеджер для кастомной модели пользователя."""

    def create_user(self, username, email, password=None, **extra_fields):
        """Создаёт и сохраняет пользователя с обязательным email."""
        if not email:
            raise ValueError('Поле email обязательно.')
        email = self.normalize_email(email)
        return super().create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Создаёт и сохраняет суперпользователя с обязательным email."""
        if not email:
            raise ValueError('Для суперпользователя обязателен email.')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True.'
            )

        email = self.normalize_email(email)
        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Строковое представление пользователя."""
        return self.username