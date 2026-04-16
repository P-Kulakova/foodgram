"""Сериализаторы для модели пользователя и подписок."""
import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import serializers


from .models import Subscription
from .validators import (
    username_validator,
    unique_email_validator,
    unique_username_validator
)

User = get_user_model()

MAX_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки изображения в формате base64."""

    def to_internal_value(self, data):
        """Преобразует base64-строку в файл изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format_part, image_str = data.split(';base64,')
            ext = format_part.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_str),
                name=f'avatar.{ext}',
            )
        return super().to_internal_value(data)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    first_name = serializers.CharField(
        required=True,
        max_length=MAX_LENGTH,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=MAX_LENGTH,
    )
    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LENGTH,
        validators=[unique_email_validator],
    )
    username = serializers.CharField(
        required=True,
        max_length=MAX_LENGTH,
        validators=[username_validator, unique_username_validator],
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        """Мета для сериализатора регистрации пользователя."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        """Создаёт пользователя с хешированием пароля."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета для сериализатора пользователя."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        """Мета для сериализатора аватара пользователя."""

        model = User
        fields = ('avatar',)


class SubscriptionUserSerializer(CustomUserSerializer):
    """Сериализатор пользователя с рецептами для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        """Мета для сериализатора пользователя с рецептами для подписок."""

        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Возвращает рецепты автора для подписок."""
        from api.serializers import RecipeShortSerializer
        request = self.context.get('request')
        recipes = obj.recipes.all()

        recipes_limit = None
        if request is not None:
            recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (TypeError, ValueError):
                pass

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов автора."""
        return obj.recipes.count()
