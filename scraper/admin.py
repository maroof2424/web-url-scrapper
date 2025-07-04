from django.contrib import admin
from .models import ScrapeHistory

@admin.register(ScrapeHistory)
class ScrapeHistoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'status', 'scraped_at', 'error_message')
    list_filter = ('status', 'scraped_at')
    search_fields = ('title', 'url', 'error_message')
    readonly_fields = ('scraped_at', 'content_json', 'error_message')
    date_hierarchy = 'scraped_at'

    def has_add_permission(self, request):
        return False  # Prevent manual creation