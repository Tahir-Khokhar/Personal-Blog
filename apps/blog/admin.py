from django.contrib import admin
from apps.blog.models import Post, Category, PostImage


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'views', 'likes_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    prepopulated_fields = {}
    date_hierarchy = 'created_at'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


class PostImageAdmin(admin.ModelAdmin):
    list_display = ['post', 'uploaded_at']
    list_filter = ['uploaded_at']


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PostImage, PostImageAdmin)
