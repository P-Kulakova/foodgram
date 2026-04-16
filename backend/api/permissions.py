"""Права доступа для рецептов, ингредиентов и тегов."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование только автору объекта."""

    def has_permission(self, request, view):
        """
        Разрешает доступ только для чтения.

        Полный доступ для авторизованных пользователей.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Разрешает редактирование только автору объекта."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
