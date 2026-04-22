"""Фильтры для рецептов, ингредиентов и тегов."""

import django_filters

from recipes.models import Ingredient, Recipe, Tag

from .const import FILTER_ENABLED, FILTER_VALUES


class IngredientFilter(django_filters.FilterSet):
    """Фильтры для ингредиентов."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        """Метаданные фильтра ингредиентов."""

        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    """Фильтры для рецептов."""

    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart',
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        """Метаданные фильтра рецептов."""

        model = Recipe
        fields = ('author', 'tags',)

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по избранному текущего пользователя."""
        if value not in FILTER_VALUES:
            return queryset

        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value == FILTER_ENABLED else queryset

        if value == FILTER_ENABLED:
            return queryset.filter(favorites__user=user).distinct()
        return queryset.exclude(favorites__user=user).distinct()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по списку покупок текущего пользователя."""
        if value not in FILTER_VALUES:
            return queryset

        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value == FILTER_ENABLED else queryset

        if value == FILTER_ENABLED:
            return queryset.filter(shopping_cart__user=user).distinct()
        return queryset.exclude(shopping_cart__user=user).distinct()
