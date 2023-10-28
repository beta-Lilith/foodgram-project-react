import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from recipes.models import Ingredient

FILE_NOT_FOUND = 'Не найден json файл в директории {}'
SUCCESS = 'Ингредиенты добавлены в базу'


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            file_path = os.path.join(settings.CSVDATA_ROOT, 'ingredients.json')
            with open(file_path, 'r', encoding='utf-8') as data:
                reader = json.load(data)
                progress_bar = tqdm(reader, total=sum(1 for _ in reader))
                data.seek(0)
                for item in progress_bar:
                    Ingredient.objects.get_or_create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit'])
        except FileNotFoundError:
            raise CommandError(FILE_NOT_FOUND.format(file_path))
        self.stdout.write(SUCCESS)
