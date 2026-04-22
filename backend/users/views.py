"""Представления для пользователей."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription
from users.serializers import (AvatarSerializer, CustomUserCreateSerializer,
                               CustomUserSerializer,
                               SubscriptionUserSerializer)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """ViewSet для пользователей."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionUserSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action in ('list', 'retrieve', 'me'):
            return CustomUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Возвращает permissions в зависимости от действия."""
        if self.action in ('create', 'list', 'retrieve'):
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    @transaction.atomic
    def avatar(self, request):
        """Добавляет, изменяет или удаляет аватар текущего пользователя."""
        if request.method == 'PUT':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            request.user.avatar = serializer.validated_data['avatar']
            request.user.save()
            return Response(
                {'avatar': request.user.avatar.url},
                status=status.HTTP_200_OK,
            )

        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя."""
        queryset = User.objects.filter(
            subscribers__user=request.user,
        ).distinct()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
    )
    @transaction.atomic
    def subscribe(self, request, id=None):
        """Подписывает на автора или отменяет подписку."""
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author,
            )
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).first()

        if subscription is None:
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
