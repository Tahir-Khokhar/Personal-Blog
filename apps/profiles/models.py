from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


IMAGE_VALIDATORS = [FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])]


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', default='default/default-user.jpg',
        null=True, blank=True, validators=IMAGE_VALIDATORS
    )
    cover_photo = models.ImageField(
        upload_to='cover_photos/', null=True, blank=True, validators=IMAGE_VALIDATORS
    )
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_date']

    def __str__(self):
        return f"{self.user.full_name or self.user.username}'s Profile"

    def followers_count(self):
        return self.user.followers.count()

    def following_count(self):
        return self.user.following.count()

    def posts_count(self):
        return self.user.posts.filter(status='Active').count()
