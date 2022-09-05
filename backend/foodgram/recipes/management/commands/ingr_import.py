import csv

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            with open('ingredients.csv', 'r', newline='',
                      encoding='utf-8') as file:
                result = csv.reader(file)

                for r in result:
                    name = r['name']
                    measurement_unit = r['measurement_unit']
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )

        except FileNotFoundError:
            raise CommandError('Файл ingredients не найден в data')
