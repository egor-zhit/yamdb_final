from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.conf import settings

from .mixins import ValidateUsername
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignupSerializer(serializers.Serializer, ValidateUsername):
    """Сериализатор нового пользователя"""

    email = serializers.EmailField(max_length=settings.EMAIL_LENGTH)
    username = serializers.CharField(max_length=settings.USERNAME_LENGTH)


class TokenSerializer(serializers.Serializer, ValidateUsername):
    """Сериализатор для получения JWT-токена"""

    username = serializers.CharField(
        required=True, allow_blank=False, max_length=settings.USERNAME_LENGTH
    )
    confirmation_code = serializers.CharField(
        max_length=settings.PINCODE_LENGTH, required=True
    )


class UserSerializer(serializers.ModelSerializer, ValidateUsername):
    """Сериализатор пользователей"""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий"""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleListSerializer(serializers.ModelSerializer):
    """Сериализатор произведения"""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'description',
            'rating',
            'year',
            'genre',
            'category',
        )

        read_only_fields = fields


class TitleSerializer(serializers.ModelSerializer):

    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'year', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор обзоров"""

    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )
    score = serializers.IntegerField(
        min_value=settings.SCORE_MIN,
        max_value=settings.SCORE_MAX,
        required=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        if (
            request.method == 'POST'
            and Review.objects.filter(
                title=get_object_or_404(
                    Title, pk=self.context['view'].kwargs.get('title_id')
                ),
                author=request.user,
            ).exists()
        ):
            raise ValidationError(
                _('Вы не можете добавить более одного отзыва')
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
