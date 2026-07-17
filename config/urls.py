"""
URL configuration for Personal Blog project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.profiles.urls')),
    path('', include('apps.blog.urls')),
    path('', include('apps.comments.urls')),
    path('', include('apps.likes.urls')),
    path('', include('apps.follows.urls')),
    path('', include('apps.notifications.urls')),
    path('', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
