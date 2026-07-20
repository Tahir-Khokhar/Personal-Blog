from django.urls import path
from apps.dashboard import views as dashboard_views

urlpatterns = [
    path('', dashboard_views.dashboard_view, name='dashboard'),
    path('posts/', dashboard_views.dashboard_posts_view, name='dashboard_posts'),
    path('comments/', dashboard_views.dashboard_comments_view, name='dashboard_comments'),
    path('notifications/', dashboard_views.dashboard_notifications_view, name='dashboard_notifications'),
]
