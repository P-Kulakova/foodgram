"""Валидация данных для рецептов, ингредиентов и тегов."""

from rest_framework import serializers


def validate_not_empty(value, field_name):
    """Проверяет, что список не пустой."""
    if not value:
        raise serializers.ValidationError(
            f'Поле "{field_name}" не должно быть пустым.'
        )
    return value


def validate_no_duplicates(value, field_name):
    """Проверяет, что в списке нет повторяющихся элементов."""
    if len(value) != len(set(value)):
        raise serializers.ValidationError(
            f'Поле "{field_name}" не должно содержать дубликаты.'
        )
    return value


def validate_tags(value):
    """Проверяет список тегов."""
    validate_not_empty(value, 'tags')

    tag_ids = [tag.id for tag in value]
    validate_no_duplicates(tag_ids, 'tags')

    return value


def validate_ingredients(value):
    """Проверяет список ингредиентов."""
    validate_not_empty(value, 'ingredients')

    ingredient_ids = [item['id'].id for item in value]
    validate_no_duplicates(ingredient_ids, 'ingredients')

    return value
