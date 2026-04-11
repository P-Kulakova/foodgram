"""Модели приложения recipes."""

from django.db import models


MAX_NAME_LENGTH = 32
MAX_SLUG_LENGTH = 32
MAX_INGREDIENT_NAME_LENGTH = 128
MAX_MEASUREMENT_UNIT_LENGTH = 64


class Tag(models.Model):
    """Модель тегов для рецептов."""

    name: models.CharField = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGTH,
        unique=True
    )
    slug: models.SlugField = models.SlugField(
        'Слаг',
        max_length=MAX_SLUG_LENGTH,
        unique=True
    )

    class Meta:
        """Метаданные модели тегов."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        """Возвращает строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name: models.CharField = models.CharField(
        'Название',
        max_length=MAX_INGREDIENT_NAME_LENGTH
    )
    measurement_unit: models.CharField = models.CharField(
        'Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        """Метаданные модели ингредиентов."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        """Строковое представление ингредиента."""
        return f'{self.name} ({self.measurement_unit})'
