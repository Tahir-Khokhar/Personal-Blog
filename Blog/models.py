from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db.models.signals import post_save
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
import shortuuid

IMAGE_VALIDATORS = [FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        username = extra.pop("username", None) or email.split("@")[0]
        user = self.model(email=email, username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=100, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.email:
            email_username = self.email.split("@")[0]
            if not self.full_name:
                self.full_name = email_username
            if not self.username:
                self.username = email_username
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image", default="default/default-user.jpg",
                              null=True, blank=True, validators=IMAGE_VALIDATORS)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    author = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.full_name or self.user.full_name)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.full_name
        super().save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="image", null=True, blank=True, validators=IMAGE_VALIDATORS)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Category"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def post_count(self):
        return Post.objects.filter(category=self).count()


class Post(models.Model):
    STATUS = (
        ("Active", "Active"),
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )



    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="image", null=True, blank=True,
                              validators=IMAGE_VALIDATORS)
    description = CKEditor5Field()
    content = CKEditor5Field(null=True, blank=True)
    tags = TaggableManager(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                 related_name='posts')
    status = models.CharField(max_length=100, choices=STATUS, default="Active")
    featured = models.BooleanField(default=False)
    view = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="likes_user")
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    publish_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Post"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["status", "-date"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "post"
            slug = f"{base}-{shortuuid.uuid()[:4]}"
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base}-{shortuuid.uuid()[:4]}"
            self.slug = slug
        super().save(*args, **kwargs)

    def comments(self):
        return Comment.objects.filter(post=self).order_by("-id")

    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                             related_name="comments")
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    comment = models.TextField()
    reply = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.post.title} - {self.name}"

    class Meta:
        verbose_name_plural = "Comment"
        ordering = ["date"]


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name_plural = "Follow"

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name_plural = "Bookmark"

    def __str__(self):
        return f"{self.post.title} - {self.user.username}"


class Notification(models.Model):
    NOTI_TYPE = (("Like", "Like"), ("Comment", "Comment"),
                 ("Bookmark", "Bookmark"), ("Follow", "Follow"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True,
                             related_name="notifications")
    type = models.CharField(max_length=100, choices=NOTI_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name_plural = "Notification"

    def __str__(self):
        if self.post:
            return f"{self.type} - {self.post.title}"
        return "Notification"

class EmailSubscription(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = "Email Subscriptions"

class Visitor(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    date = models.DateField()
    count = models.IntegerField(default=1)

    class Meta:
        unique_together = ('session_key', 'date')

def send_new_post_email(post):
    subscribers = EmailSubscription.objects.filter(is_active=True)
    subject = f"New Post: {post.title}"
    for sub in subscribers:
        html_message = render_to_string(
            'emails/new_post.html',
            {'post': post, 'email': sub.email, 'site_url': settings.SITE_URL},
        )
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [sub.email],
            html_message=html_message,
            fail_silently=True,
        )
