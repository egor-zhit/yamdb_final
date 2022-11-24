import re
from datetime import datetime as dt

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

FORBIDDEN_USERNAMES = ('me',)
LEGAL_CHARACTERS = re.compile(r'[\w.@+-]')


def username_validator(value):
    """Проверка на запрещенные слова в имени."""
    forbidden_chars = ''.join(set(LEGAL_CHARACTERS.sub('', value)))
    if forbidden_chars:
        raise ValidationError(
            f'Нельзя использовать символ(ы): {forbidden_chars} в имени '
            f'пользователя.'
        )
    if value in FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Использовать {value} в качестве имени пользователя запрещено.'
        )
    return value


def year_validator(value):
    if value > dt.now().year:
        raise ValidationError(
            _(
                f'Нельзя добавлять произведения, которые еще не вышли.'
                f'Год выпуска ({value}) не может быть больше текущего.'
            )
        )
    return value
