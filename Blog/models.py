from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Post Model
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    content = models.TextField()

    image = models.ImageField(upload_to='posts/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(User, related_name="likes", blank=True)

    def __str__(self):
        return self.title


# Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    text = models.TextField()

    created_at=models.DateTimeField(auto_now_add=True)
