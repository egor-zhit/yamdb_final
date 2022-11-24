from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User

EMPTY_VALUE = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование юзеров"""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    list_editable = ('role',)
    search_fields = ('username', 'email')
    list_filter = ('role',)
    empty_value_display = EMPTY_VALUE


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Администрирование категорий"""

    list_display = ('id', 'name', 'slug')
    search_fields = ('slug',)
    empty_value_display = EMPTY_VALUE
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Администрирование жанров"""

    list_display = ('id', 'name', 'slug')
    search_fields = ('slug',)
    empty_value_display = EMPTY_VALUE
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Администрирование произведений"""

    list_display = ('id', 'name', 'description', 'year', 'category')
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = EMPTY_VALUE


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Администрирование обзоров"""

    list_display = ('id', 'author', 'text', 'pub_date', 'title', 'score')
    search_fields = ('title', 'author')
    list_filter = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Администрирование комментариев"""

    list_display = ('id', 'author', 'text', 'pub_date', 'review')
    search_fields = ('text',)
    list_filter = ('author',)
