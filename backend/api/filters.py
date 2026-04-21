"""Фильтры для рецептов, ингредиентов и тегов."""

import django_filters
from recipes.models import Recipe, Tag

FILTER_ENABLED = 1
FILTER_DISABLED = 0


class RecipeFilter(django_filters.FilterSet):
    """Фильтры для рецептов."""

    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        """Метаданные фильтра рецептов."""

        model = Recipe
        fields = ('author', 'tags')

    def _filter_by_user_relationship(
        self, queryset, value, relationship_field
    ):
        """Фильтрует рецепты по отношению пользователя к рецепту."""
        if self.request is None:
            return queryset

        user = self.request.user
        if not user.is_authenticated:
            return (
                queryset.none() if value == FILTER_ENABLED else queryset
            )

        filter_field = f'{relationship_field}__user'
        if value == FILTER_ENABLED:
            return queryset.filter(**{filter_field: user}).distinct()
        if value == FILTER_DISABLED:
            return queryset.exclude(**{filter_field: user}).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по избранному текущего пользователя."""
        return self._filter_by_user_relationship(queryset, value, 'favorites')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по списку покупок текущего пользователя."""
        return self._filter_by_user_relationship(
            queryset, value, 'shopping_cart'
        )
