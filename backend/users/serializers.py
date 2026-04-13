"""Сериализаторы для модели пользователя и подписок."""

from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer,
)
from rest_framework import serializers

from recipes.models import Recipe
from .models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки картинки в формате base64."""

    def to_internal_value(self, data):
        """Преобразование base64 строки в изображение."""
        if isinstance(data, str) and data.startswith('data:image'):
            format_part, image_str = data.split(';base64,')
            ext = format_part.split('/')[-1]

            from base64 import b64decode
            from django.core.files.base import ContentFile

            data = ContentFile(
                b64decode(image_str),
                name=f'temp.{ext}',
            )
        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для подписок."""

    class Meta:
        """Метаданные сериализатора рецепта для подписок."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор регистрации пользователя."""

    class Meta(DjoserUserCreateSerializer.Meta):
        """Метаданные сериализатора регистрации пользователя."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        """Метаданные сериализатора пользователя."""

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
        """Проверяет, есть ли уже подписка."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения аватара."""

    avatar = Base64ImageField()

    class Meta:
        """Метаданные сериализатора для добавления и изменения аватара."""

        model = User
        fields = ('avatar',)


class SubscriptionUserSerializer(CustomUserSerializer):
    """Сериализатор пользователя с рецептами для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        """Метаданные сериализатора пользователя с рецептами для подписок."""

        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Получает рецепты автора для отображения в подписках."""
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
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        """Получает количество рецептов автора для отображения в подписках."""
        return obj.recipes.count()
