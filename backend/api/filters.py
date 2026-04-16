"""Фильтры для рецептов, ингредиентов и тегов."""

from recipes.models import Recipe, Tag
import django_filters


FILTER_ENABLED = 1
FILTER_DISABLED = 0


class RecipeFilter(django_filters.FilterSet):
    """Фильтры для рецептов."""

    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
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

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по избранному текущего пользователя."""
        request = self.request
        if request is None:
            return queryset

        user = request.user
        if not user.is_authenticated:
            if value == FILTER_ENABLED:
                return queryset.none()
            return queryset

        if value == FILTER_ENABLED:
            return queryset.filter(favorites__user=user).distinct()
        if value == FILTER_DISABLED:
            return queryset.exclude(favorites__user=user).distinct()

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по списку покупок текущего пользователя."""
        request = self.request
        if request is None:
            return queryset

        user = request.user
        if not user.is_authenticated:
            if value == FILTER_ENABLED:
                return queryset.none()
            return queryset

        if value == FILTER_ENABLED:
            return queryset.filter(shopping_cart__user=user).distinct()
        if value == FILTER_DISABLED:
            return queryset.exclude(shopping_cart__user=user).distinct()

        return queryset
