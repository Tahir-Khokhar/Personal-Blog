from django.urls import path
from apps.profiles import views as profiles_views

urlpatterns = [
    path('profile/', profiles_views.profile_view, name='profile'),
    path('profile/edit/', profiles_views.edit_profile_view, name='edit_profile'),
    path('user/<str:username>/', profiles_views.author_profile_view, name='author_profile'),
]
