import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Tag

FILE_NOT_FOUND = 'Не найден json файл в директории {}'
SUCCESS = 'Теги добавлены в базу'


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            file_path = os.path.join(settings.CSVDATA_ROOT, 'tags.json')
            with open(file_path, 'r', encoding='utf-8') as data:
                reader = json.load(data)
                Tag.objects.bulk_create(
                    Tag(
                        name=item['name'],
                        color=item['color'], slug=item['slug'])
                    for item in reader)
        except FileNotFoundError:
            raise CommandError(FILE_NOT_FOUND.format(file_path))
        self.stdout.write(SUCCESS)
