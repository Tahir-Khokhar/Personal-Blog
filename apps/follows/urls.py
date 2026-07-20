from django.urls import path
from apps.follows import views as follows_views

urlpatterns = [
    path('follow/<str:username>/', follows_views.toggle_follow_view, name='toggle_follow'),
]
