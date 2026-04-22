"""Валидаторы для пользователей."""

from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator

from .models import User

USERS_QUERYSET = User.objects.all()

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Введите корректное имя пользователя.'
)

unique_email_validator = UniqueValidator(
    queryset=USERS_QUERYSET,
    message='Пользователь с таким email уже существует.'
)

unique_username_validator = UniqueValidator(
    queryset=USERS_QUERYSET,
    message='Пользователь с таким username уже существует.'
)
