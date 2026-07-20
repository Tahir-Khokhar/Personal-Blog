import shortuuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.utils.text import slugify
from django.utils import timezone
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field


USER = settings.AUTH_USER_MODEL



IMAGE_VALIDATORS = [FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])]


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True, validators=IMAGE_VALIDATORS)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def post_count(self):
        return self.posts.filter(status='Active').count()


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', db_index=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)
    content = CKEditor5Field()
    excerpt = models.TextField(null=True, blank=True)
    featured_image = models.ImageField(
        upload_to='posts/', null=True, blank=True, validators=IMAGE_VALIDATORS
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = TaggableManager(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'post'
            slug = f"{base}-{shortuuid.uuid()[:4]}"
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base}-{shortuuid.uuid()[:4]}"
            self.slug = slug
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(views=models.F('views') + 1)

    def increment_likes(self):
        Post.objects.filter(pk=self.pk).update(likes_count=models.F('likes_count') + 1)

    def decrement_likes(self):
        Post.objects.filter(pk=self.pk).update(likes_count=models.F('likes_count') - 1)

    def increment_comments(self):
        Post.objects.filter(pk=self.pk).update(comments_count=models.F('comments_count') + 1)

    def decrement_comments(self):
        Post.objects.filter(pk=self.pk).update(comments_count=models.F('comments_count') - 1)

    def increment_shares(self):
        Post.objects.filter(pk=self.pk).update(shares_count=models.F('shares_count') + 1)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/gallery/', validators=IMAGE_VALIDATORS)
    caption = models.CharField(max_length=200, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Image for {self.post.title}"
