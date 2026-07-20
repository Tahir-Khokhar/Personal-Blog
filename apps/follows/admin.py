from django.contrib import admin
from apps.follows.models import Follow


class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']


admin.site.register(Follow, FollowAdmin)
