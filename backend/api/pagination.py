"""Пагинации в API."""

from rest_framework.pagination import PageNumberPagination


class LimitPagePagination(PageNumberPagination):
    """Пагинация с параметром limit."""

    page_size = 6
    page_size_query_param = 'limit'
