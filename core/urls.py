from django.urls import path
from core import views as core_views

urlpatterns = [
    path('', core_views.home_view, name='home'),
]
