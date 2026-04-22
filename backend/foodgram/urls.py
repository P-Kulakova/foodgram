"""URL-адреса для проекта Foodgram."""

from api.short_link import short_link_redirect
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('api.urls')),
    path('r/<int:id>/', short_link_redirect),
]
