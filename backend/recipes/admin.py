"""
Админка для моделей.

Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart.
"""

from django.contrib import admin
from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Админка для модели RecipeIngredient внутри модели Recipe."""

    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""

    list_display = ('id', 'name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для модели Favorite."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для модели ShoppingCart."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
