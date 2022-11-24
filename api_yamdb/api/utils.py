from random import sample

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

PINCODE_CHARS = '0123456789'


def make_pin():
    """Создание пинкода."""
    return ''.join(sample(PINCODE_CHARS, settings.PINCODE_LENGTH))


def send_pincode(user, pincode):
    """Отправка пинкода."""
    send_mail(
        _('Код подтверждения API YaMDb'),
        _(
            f'Здравствуйте, {user.username}!\n\n'
            f'Ваш код подтверждения для получения доступа к API:\n'
            f'{pincode}'
        ),
        settings.EMAIL_REPLY_TO,
        [user.email],
    )
