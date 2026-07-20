from django.urls import path
from apps.likes import views as likes_views

urlpatterns = [
    path('post/<slug:slug>/like/', likes_views.toggle_like_view, name='toggle_like'),
]
