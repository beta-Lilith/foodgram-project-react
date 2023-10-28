import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

FILE_NOT_FOUND = 'Не найден json файл в директории {}'
SUCCESS = 'Ингредиенты добавлены в базу'


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            file_path = os.path.join(settings.CSVDATA_ROOT, 'ingredients.json')
            with open(file_path, 'r', encoding='utf-8') as data:
                reader = json.load(data)
                Ingredient.objects.bulk_create(
                    Ingredient(
                        name=item['name'],
                        measurement_unit=item['measurement_unit'])
                    for item in reader)
        except FileNotFoundError:
            raise CommandError(FILE_NOT_FOUND.format(file_path))
        self.stdout.write(SUCCESS)
