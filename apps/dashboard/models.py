from django.db import models
from django.conf import settings


class DashboardStats(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard_stats')
    total_posts = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_followers = models.PositiveIntegerField(default=0)
    total_bookmarks = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dashboard Stats'

    def __str__(self):
        return f"Stats for {self.user.username}"
