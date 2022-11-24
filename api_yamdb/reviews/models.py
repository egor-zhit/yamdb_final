from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .validators import username_validator, year_validator

ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'
ROLES = (
    (ROLE_USER, _('Пользователь')),
    (ROLE_MODERATOR, _('Модератор')),
    (ROLE_ADMIN, _('Администратор')),
)


class User(AbstractUser):
    """Кастомная модель пользователей."""

    username = models.CharField(
        _('username'),
        max_length=settings.USERNAME_LENGTH,
        unique=True,
        validators=(username_validator,),
    )
    email = models.EmailField(
        _('email address'), max_length=settings.EMAIL_LENGTH, unique=True
    )
    first_name = models.CharField(
        _('first name'), max_length=settings.USER_FIRSTNAME_LENGTH, blank=True
    )
    last_name = models.CharField(
        _('last name'), max_length=settings.USER_LASTNAME_LENGTH, blank=True
    )
    bio = models.TextField(_('биография'), blank=True)
    role = models.CharField(
        _('роль'),
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=ROLE_USER,
    )
    pincode = models.CharField(
        max_length=settings.PINCODE_LENGTH,
        default=settings.DEFAULT_PINCODE,
    )

    @property
    def is_admin(self):
        return self.is_staff or self.role == ROLE_ADMIN

    @property
    def is_moderator(self):
        return self.role == ROLE_MODERATOR


class CategoryGenreCommon(models.Model):
    """Абстрактная модель для DRI"""

    name = models.CharField(max_length=settings.CATEGORY_GENRE_LENGTH)
    slug = models.SlugField(unique=True, max_length=settings.SLUG_LENGTH)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryGenreCommon):
    """Модель для категории произведения"""

    class Meta(CategoryGenreCommon.Meta):
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')


class Genre(CategoryGenreCommon):
    """Модель для жанра произведения"""

    class Meta(CategoryGenreCommon.Meta):
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')


class Title(models.Model):
    """Модель произведения."""

    MODEL_STRING = (
        '{name:.30} ({description:.30}) '
        'жанра {genre} в категории {category} {year} года'
    )

    name = models.TextField(_('Название'))
    description = models.TextField(_('Описание'), blank=True)
    year = models.IntegerField(
        _('Год выпуска'), blank=True, validators=(year_validator,)
    )
    genre = models.ManyToManyField(
        Genre, verbose_name=_('Жанр'), related_name='titles', blank=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_('Категория'),
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('Произведение')
        verbose_name_plural = _('Произведения')

    def __str__(self):
        return self.MODEL_STRING.format(
            name=self.name,
            description=self.description,
            genre=self.genre,
            category=self.category,
            year=self.year,
        )


class ReviewCommentCommon(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    author = models.ForeignKey(
        User, verbose_name=_('Автор'), on_delete=models.CASCADE
    )
    text = models.TextField(_('Текст'))
    pub_date = models.DateTimeField(
        _('Дата публикации'), auto_now_add=True, db_index=True
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:30]


class Review(ReviewCommentCommon):
    """Модель отзывов пользователей."""

    MIN_MAX_ERROR_MSG = _(
        f'Допустимы значения от {settings.SCORE_MIN} до {settings.SCORE_MAX}'
    )

    title = models.ForeignKey(
        Title, verbose_name=_('Произведение'), on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField(
        verbose_name=_('Оценка'),
        validators=[
            MinValueValidator(settings.SCORE_MIN, MIN_MAX_ERROR_MSG),
            MaxValueValidator(settings.SCORE_MAX, MIN_MAX_ERROR_MSG),
        ],
    )

    class Meta(ReviewCommentCommon.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique_reviews'
            )
        ]
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')


class Comment(ReviewCommentCommon):
    """Модель комментариев пользователей."""

    review = models.ForeignKey(
        Review, verbose_name=_('Обзор'), on_delete=models.CASCADE
    )

    class Meta(ReviewCommentCommon.Meta):
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
