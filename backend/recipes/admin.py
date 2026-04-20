"""
Админка для моделей.

Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart.
"""

from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Админка для модели RecipeIngredient внутри модели Recipe."""

    model = RecipeIngredient
    extra = 1


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка для модели RecipeIngredient."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ('recipe', 'ingredient')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""

    list_display = ('name', 'author', 'favorites_count')
    search_fields = (
        'name',
        'author__username',
        'author__email',
        'author__first_name',
        'author__last_name',
    )
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('favorites_count',)

    def get_queryset(self, request):
        """Оптимизирует queryset для списка рецептов."""
        queryset = super().get_queryset(request)
        return (
            queryset.select_related('author')
            .prefetch_related('tags')
            .annotate(favorites_total=Count('favorites'))
        )

    @admin.display(description='В избранном', ordering='favorites_total')
    def favorites_count(self, obj):
        """Возвращает число добавлений рецепта в избранное."""
        return obj.favorites_total


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для модели Favorite."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для модели ShoppingCart."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
