from django.db import models
from django.conf import settings


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'post']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"

