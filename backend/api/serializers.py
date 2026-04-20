"""Сериализаторы для API."""

import base64

from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .validators import validate_ingredients, validate_tags

MIN_AMOUNT = 1
BASE64_EXT_INDEX = -1


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки изображения в формате base64."""

    def to_internal_value(self, data):
        """Преобразует base64-строку в файл изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format_part, image_str = data.split(';base64,')
            ext = format_part.split('/')[BASE64_EXT_INDEX]
            data = ContentFile(
                base64.b64decode(image_str),
                name=f'recipe.{ext}',
            )
        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецепта для подписок."""

    class Meta:
        """Сериализатор для отображения рецептов в подписках."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        """Мета-класс для отображения тегов."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        """Мета-класс для отображения ингредиентов."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиент в составе рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Мета-класс для отображения ингредиентов в рецепте."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для чтения."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        """Мета-класс для отображения рецепта."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Проверяет, находится ли рецепт в избранном у пользователя."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в списке покупок у пользователя."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class IngredientAmountSerializer(serializers.Serializer):
    """Сериализатор ингредиента для записи в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для записи."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        """Мета-класс для отображения рецепта."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def _create_ingredients(self, recipe, ingredients_data):
        """Создаёт связи рецепта с ингредиентами."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=item['id'],
                    amount=item['amount']
                )
                for item in ingredients_data
            ]
        )

    def create(self, validated_data):
        """Создаёт рецепт."""
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        tags = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_ingredients(instance, ingredients_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает рецепт в формате сериализатора чтения."""
        return RecipeSerializer(instance, context=self.context).data

    def validate_tags(self, value):
        """Проверяет список тегов."""
        return validate_tags(value)

    def validate_ingredients(self, value):
        """Проверяет список ингредиентов."""
        return validate_ingredients(value)

    def validate(self, data):
        """Проверяет наличие обязательных полей при обновлении рецепта."""
        request = self.context.get('request')

        if request and request.method in ('PUT', 'PATCH'):
            if 'ingredients' not in self.initial_data:
                raise serializers.ValidationError(
                    {'ingredients': 'Обязательное поле.'}
                )
            if 'tags' not in self.initial_data:
                raise serializers.ValidationError(
                    {'tags': 'Обязательное поле.'}
                )
        return data
