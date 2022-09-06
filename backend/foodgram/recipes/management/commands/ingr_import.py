import csv

from django.core.management import BaseCommand
# Import the model
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('./data/ingredients.csv', 'r',
                  encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    unit=unit)
