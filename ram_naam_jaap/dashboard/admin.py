from django.contrib import admin
from .models import Target, Achievement


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_target', 'weekly_target', 'monthly_target', 'yearly_target', 'updated_at')
    list_filter = ('user', 'updated_at')
    search_fields = ('user__username', 'user__email')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_type', 'title', 'achieved_at')
    list_filter = ('achievement_type', 'achieved_at')
    search_fields = ('user__username', 'user__email', 'title', 'description')
    date_hierarchy = 'achieved_at'
