"""URL-адреса для проекта Foodgram."""

from django.contrib import admin
from django.urls import include, path

from api.short_link import short_link_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('api.urls')),
    path('s/<int:id>/', short_link_redirect),
]
