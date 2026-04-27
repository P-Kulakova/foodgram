"""Сериализаторы для модели пользователя и подписок."""

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .const import EMAIL_MAX_LENGTH, USER_FIELDS_MAX_LENGTH
from .models import Subscription, User
from .validators import (unique_email_validator, unique_username_validator,
                         username_validator)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    first_name = serializers.CharField(
        required=True,
        max_length=USER_FIELDS_MAX_LENGTH,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=USER_FIELDS_MAX_LENGTH,
    )
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
        validators=[unique_email_validator],
    )
    username = serializers.CharField(
        required=True,
        max_length=USER_FIELDS_MAX_LENGTH,
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

    @transaction.atomic
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
        """Мета для сериализатора пользователя с рецептами."""

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
