"""Админка для моделей User и Subscription."""

from django.contrib import admin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели User."""

    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('email',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для модели Subscription."""

    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
