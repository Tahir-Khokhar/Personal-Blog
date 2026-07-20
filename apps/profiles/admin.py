from django.contrib import admin
from apps.profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email', 'user__full_name']
    list_display = ['user', 'location', 'gender', 'joined_date']
    list_select_related = ['user']
    list_filter = ['gender', 'joined_date']


admin.site.register(Profile, ProfileAdmin)
