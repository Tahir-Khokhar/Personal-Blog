from django.contrib import admin
from apps.accounts.models import User, OTPRequest


class UserAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username', 'email']
    list_display = ['username', 'email', 'full_name', 'is_email_verified', 'is_staff']
    list_filter = ['is_staff', 'is_active', 'is_email_verified']


class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']


admin.site.register(User, UserAdmin)
admin.site.register(OTPRequest, OTPRequestAdmin)
