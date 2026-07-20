from django.contrib import admin
from apps.notifications.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'post', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'post__title', 'message']


admin.site.register(Notification, NotificationAdmin)
