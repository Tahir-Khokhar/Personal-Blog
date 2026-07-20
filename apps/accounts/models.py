import random
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings


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
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=100, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

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

    def generate_otp(self):
        self.otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp

    def is_otp_valid(self, otp):
        if not self.otp or not self.otp_created_at:
            return False
        if self.otp != otp:
            return False
        if timezone.now() > self.otp_created_at + timedelta(minutes=5):
            return False
        return True

    def clear_otp(self):
        self.otp = None
        self.otp_created_at = None
        self.save()

    def is_account_locked(self):
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        if self.account_locked_until and timezone.now() >= self.account_locked_until:
            self.account_locked_until = None
            self.failed_login_attempts = 0
            self.save()
        return False

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timedelta(minutes=15)
        self.save()

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()


class OTPRequest(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        return (
            not self.is_used
            and self.created_at >= timezone.now() - timedelta(minutes=5)
        )

    def __str__(self):
        return f"{self.email} - {self.otp}"
