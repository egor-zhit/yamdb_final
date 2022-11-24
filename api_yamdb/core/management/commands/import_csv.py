import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, Review, Title, User

MODEL_FILENAME = (
    (User, 'users.csv'),
    (Category, 'category.csv'),
    (Genre, 'genre.csv'),
    (Title, 'titles.csv'),
    (Review, 'review.csv'),
    (Comment, 'comments.csv'),
    (Title.genre.through, 'genre_title.csv'),
)

# В исходных таблицах некоторые поля названы неподходящим образом, исправления
# задаются в FIELD_RENAME
FIELD_RENAME = (('author', 'author_id'), ('category', 'category_id'))


class Command(BaseCommand):
    """Импортирование данных из CSV файлов в модель"""

    help = (
        'Импортирует CSV файлы БД из директории static/data'
    )

    def handle(self, *args, **options):
        working_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        if not os.path.isdir(working_dir):
            raise CommandError('Директории static/data не существует.')

        for model, file in MODEL_FILENAME:
            with open(
                os.path.join(working_dir, file), 'r', encoding='utf-8'
            ) as f:
                reader = csv.DictReader(f, delimiter=',')
                model.objects.all().delete()
                objects = []
                for data in reader:
                    for csv_field_name, model_field_name in FIELD_RENAME:
                        try:
                            data[model_field_name] = data.pop(csv_field_name)
                        except KeyError:
                            pass
                    objects.append(model(**data))
            model.objects.bulk_create(objects)
