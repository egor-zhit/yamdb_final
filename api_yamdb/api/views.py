from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminModeratorAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleListSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)
from reviews.models import Category, Genre, Review, Title
from .utils import make_pin, send_pincode

User = get_user_model()


class Signup(APIView):
    """Регистрация нового пользователя."""

    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, created = User.objects.get_or_create(
                **serializer.validated_data
            )
        # Так как у нас поля email и username уникальные,
        # если существует юзер с таким email или с таким username, то
        # метод get_or_create выбросит исключение IntegrityError,
        except IntegrityError:
            return Response(
                {'username': _('Пользователь с такими данными уже есть.')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pincode = make_pin()
        send_pincode(user, pincode)
        user.pincode = pincode
        user.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class Token(APIView):
    """Генерация токена для юзера с кодом подтверждения."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=request.data['username'])
        if (
            user.pincode != settings.DEFAULT_PINCODE
            and user.pincode == serializer.data['confirmation_code']
        ):
            return Response(
                {'token': str(RefreshToken.for_user(user).access_token)},
                status=status.HTTP_201_CREATED,
            )
        # Пинкод сбрасываем на дефолтный, в случае если передан неверный,
        # чтобы избежать подбора
        user.pincode = settings.DEFAULT_PINCODE
        user.save()
        return Response(
            {
                'confirmation_code': _(
                    'Неверный код подтверждения. Запросите новый.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserViewSet(viewsets.ModelViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=('GET', 'PATCH'),
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=None,
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(
                UserSerializer(request.user).data, status=status.HTTP_200_OK
            )
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CategoryGenreCommonViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вью-сет для DRI"""

    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('name',)
    search_fields = ('name',)


class GenreViewSet(CategoryGenreCommonViewSet):
    """Жанры"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreCommonViewSet):
    """Категории"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Произведение"""

    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    list_serializer_class = TitleListSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = TitleFilter
    ordering = ('name', '-rating')
    ordering_fields = ('name', 'rating', 'year')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return self.list_serializer_class
        return self.serializer_class
