"""Админка для моделей User и Subscription."""

from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели User."""

    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('email',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для модели Subscription."""

    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
