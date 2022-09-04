import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = 'ingredients.csv'
        with open(path, 'r', newline='', encoding='utf-8') as data:
            result = csv.DictReader(data, delimiter=',')
            for line in result:
                try:
                    name = line['name']
                    measurement_unit = line['measurement_unit']
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                except Exception as ing_error:
                    print(
                        f'ошибка продукта {name}: {ing_error}'
                    )
        path = 'tags.csv'
        with open(path, 'r', newline='', encoding='utf-8') as data:
            result = csv.DictReader(data, delimiter=',')
            for line in result:
                try:
                    name = line['name']
                    color = line['color']
                    slug = line['slug']
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug,
                    )
                except Exception as tag_error:
                    print(f'ошибка тега {name}: {tag_error}')
