from django.contrib import admin
from apps.dashboard.models import DashboardStats


class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_posts', 'total_views', 'total_likes', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username']


admin.site.register(DashboardStats, DashboardStatsAdmin)
