"""Представления API приложения."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import LimitPagePagination
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)


SHOPPING_CART_LINE_START = 1


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов."""

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Возвращает queryset ингредиентов с фильтрацией по имени."""
        queryset = Ingredient.objects.all()
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPagePagination

    def get_queryset(self):
        """Возвращает queryset рецептов."""
        return Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ('create', 'partial_update', 'update'):
            return RecipeWriteSerializer
        return RecipeSerializer

    def _add_to_user_list(self, model, user, recipe):
        """Добавляет рецепт в пользовательский список."""
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe,
            context={'request': self.request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_user_list(self, model, user, recipe):
        """Удаляет рецепт из пользовательского списка."""
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response(
                {'errors': 'Рецепт отсутствует в списке.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._add_to_user_list(Favorite, request.user, recipe)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._remove_from_user_list(Favorite, request.user, recipe)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._add_to_user_list(ShoppingCart, request.user, recipe)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._remove_from_user_list(ShoppingCart, request.user, recipe)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок."""
        ingredients = {}

        recipe_ingredients = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).prefetch_related('recipe_ingredients__ingredient')

        for recipe in recipe_ingredients:
            for item in recipe.recipe_ingredients.all():
                ingredient = item.ingredient
                key = (ingredient.name, ingredient.measurement_unit)
                ingredients[key] = ingredients.get(key, 0) + item.amount

        lines = ['Список покупок:\n']
        for index, ((name, unit), amount) in enumerate(
            ingredients.items(),
            start=SHOPPING_CART_LINE_START,
        ):
            lines.append(f'{index}. {name} — {amount} {unit}\n')

        response = HttpResponse(
            ''.join(lines),
            content_type='text/plain',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=('get',),
        permission_classes=(AllowAny,),
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Возвращает ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/recipes/{recipe.id}/')

        return Response(
            {'short-link': short_link},
            status=status.HTTP_200_OK,
        )
