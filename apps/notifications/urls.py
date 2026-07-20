from django.urls import path
from apps.notifications import views as notifications_views
from django.shortcuts import get_object_or_404

urlpatterns = [
    path('', notifications_views.notifications_view, name='notifications'),
    path('<int:notification_id>/read/', notifications_views.mark_as_read_view, name='mark_notification_read'),
    path('mark-all-read/', notifications_views.mark_all_as_read_view, name='mark_all_notifications_read'),
]
