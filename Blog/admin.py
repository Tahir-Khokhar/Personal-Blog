from django.contrib import admin
from Blog import models as Blog_models

# Customize user model display and search in Django admin.
class UserAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username', 'email']
    list_display = ['username', 'email']

# Customize profile model display and search in Django admin.
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email', 'full_name']
    list_display = ['user', 'full_name', 'author', 'country']
    list_select_related = ['user']

# Display category title in the admin panel.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]

# Display post details in the admin panel.
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "category", "status", "view", "date"]

# Display comment details in the admin panel.
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "name", "email", "comment", "is_approved"]

# Display follow relationships in the admin panel.
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower", "following", "date"]

# Display bookmarked posts in the admin panel.
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "post"]

# Display notification details in the admin panel.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "type", "seen"]

# Display email subscriptions in the admin panel.
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["email", "is_active", "date"]

# Display visitor session information in the admin panel.
class VisitorAdmin(admin.ModelAdmin):
    list_display = ["session_key", "date", "count"]

# Register all blog models with their admin configurations.
admin.site.register(Blog_models.User, UserAdmin)
admin.site.register(Blog_models.Profile, ProfileAdmin)
admin.site.register(Blog_models.Category, CategoryAdmin)
admin.site.register(Blog_models.Post, PostAdmin)
admin.site.register(Blog_models.Comment, CommentAdmin)
admin.site.register(Blog_models.Notification, NotificationAdmin)
admin.site.register(Blog_models.Follow, FollowAdmin)
admin.site.register(Blog_models.Bookmark, BookmarkAdmin)
admin.site.register(Blog_models.EmailSubscription, EmailSubscriptionAdmin)
admin.site.register(Blog_models.Visitor, VisitorAdmin)
