from django.contrib import admin
from apps.bookmarks.models import Bookmark


class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']


admin.site.register(Bookmark, BookmarkAdmin)
