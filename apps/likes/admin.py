from django.contrib import admin
from apps.likes.models import Like


class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']


admin.site.register(Like, LikeAdmin)
