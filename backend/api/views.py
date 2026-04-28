"""Представления API приложения."""

from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)

from .const import SHOPPING_CART_LINE_START
from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPagePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


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
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit'),
        ).annotate(
            total_amount=Sum('amount')
        ).order_by(
            'name',
            'measurement_unit',
        )

        lines = ['Список покупок:\n']
        for index, ingredient in enumerate(
            ingredients,
            start=SHOPPING_CART_LINE_START,
        ):
            name = ingredient['name']
            unit = ingredient['measurement_unit']
            amount = ingredient['total_amount']
            lines.append(f'{index}. {name} — {amount} {unit}\n')

        response = HttpResponse(
            ''.join(lines),
            content_type='text/plain; charset=utf-8',
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
        """Получает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)

        short_link = request.build_absolute_uri(f'/s/{recipe.id}')

        return Response(
            {'short-link': short_link},
            status=status.HTTP_200_OK,
        )
