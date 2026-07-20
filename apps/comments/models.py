from django.db import models
from django.conf import settings


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"

    def save(self, *args, **kwargs):
        if not self.name and self.user_id:
            self.name = self.user.full_name or self.user.username
        if not self.email and self.user_id:
            self.email = self.user.email
        super().save(*args, **kwargs)

