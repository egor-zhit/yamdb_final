from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title='YaMDb API',
        default_version='v1',
        description='YaMDb REST API',
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticatedOrReadOnly],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc',
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
]
