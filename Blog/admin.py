from django.contrib import admin
from Blog import models as Blog_models

class UserAdmin(admin.ModelAdmin):
    search_fields  = ['full_name', 'username', 'email']
    list_display  = ['username', 'email']

class ProfileAdmin(admin.ModelAdmin):
    search_fields  = ['user']
    list_display = ['thumbnail', 'user', 'full_name']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]

class PostAdmin(admin.ModelAdmin):
    list_display = ["title","user","category","view"]

class CommentAdmin(admin.ModelAdmin):
    list_display = ["post","name","email","comment"]

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user","post"]

class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user","post","type","seen",]

admin.site.register(Blog_models.User, UserAdmin)
admin.site.register(Blog_models.Profile, ProfileAdmin)
admin.site.register(Blog_models.Category, CategoryAdmin)
admin.site.register(Blog_models.Post, PostAdmin)
admin.site.register(Blog_models.Comment, CommentAdmin)
admin.site.register(Blog_models.Notification, NotificationAdmin)
admin.site.register(Blog_models.Bookmark, BookmarkAdmin)
