"""Команда для импорта ингредиентов из CSV или JSON файлов."""

import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиентов из CSV или JSON файлов."""

    help = 'Импорт ингредиентов из CSV или JSON'

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к файлу (csv или json)',
        )

    def handle(self, *args, **options):
        """Обрабатывает команду импорта ингредиентов."""
        path = options.get('path')

        if not path:
            self.stdout.write(
                self.style.ERROR('Укажи путь к файлу через --path')
            )
            return

        file_path = Path(path)

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR('Файл не найден')
            )
            return

        if file_path.suffix == '.csv':
            self.import_csv(file_path)
        elif file_path.suffix == '.json':
            self.import_json(file_path)
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Поддерживаются только .csv и .json'
                )
            )

    @transaction.atomic
    def import_csv(self, file_path):
        """Импортирует ингредиенты из CSV файла."""
        created = 0

        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                obj, was_created = Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'],
                )
                if was_created:
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(f'CSV импорт завершён. Создано: {created}')
        )

    @transaction.atomic
    def import_json(self, file_path):
        """Импортирует ингредиенты из JSON файла."""
        created = 0

        with open(file_path, encoding='utf-8') as file:
            data = json.load(file)

            for item in data:
                obj, was_created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'],
                )
                if was_created:
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(f'JSON импорт завершён. Создано: {created}')
        )
