import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from tqdm import tqdm

from recipes.models import Ingredient

INTEGRITY_ERR = 'Ингридиет {name} уже есть в базе'
FILE_NOT_FOUND = 'Не найден CSV файл в директории {file_path}'
SUCCESS = 'CSV файл успешно импортирован'


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            file_path = os.path.join(settings.CSVDATA_ROOT, 'ingredients.csv')
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                progress_bar = tqdm(reader, total=sum(1 for _ in reader))
                csv_file.seek(0)
                for row in progress_bar:
                    try:
                        name, measurement_unit = row
                        Ingredient.objects.get_or_create(
                            name=name, measurement_unit=measurement_unit)
                    except IntegrityError:
                        self.stdout.write(INTEGRITY_ERR.format(name=name))
        except FileNotFoundError:
            raise CommandError(FILE_NOT_FOUND.format(file_path=file_path))
        self.stdout.write(SUCCESS)
