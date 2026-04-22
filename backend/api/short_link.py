"""Коротка ссылка для рецепта."""

from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def short_link_redirect(request, id):
    """Перенаправление с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, id=id)
    return redirect(f'/recipes/{recipe.id}')
