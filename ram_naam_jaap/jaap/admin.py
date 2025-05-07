from django.contrib import admin
from .models import JaapSession, JaapCount, JaapEntry, CityJaapCount


@admin.register(JaapSession)
class JaapSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'count')
    list_filter = ('user', 'start_time')
    search_fields = ('user__username',)
    date_hierarchy = 'start_time'


@admin.register(JaapCount)
class JaapCountAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'count', 'cumulative_count')
    list_filter = ('user', 'date')
    search_fields = ('user__username',)
    date_hierarchy = 'date'


@admin.register(JaapEntry)
class JaapEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'count', 'created_at')
    list_filter = ('user', 'date')
    search_fields = ('user__username',)
    date_hierarchy = 'date'


@admin.register(CityJaapCount)
class CityJaapCountAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'count', 'date', 'timestamp')
    list_filter = ('country', 'date')
    search_fields = ('city', 'country')
    date_hierarchy = 'date'
