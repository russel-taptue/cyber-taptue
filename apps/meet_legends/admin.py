from django.contrib import admin

from .models import Legend


@admin.register(Legend)
class LegendAdmin(admin.ModelAdmin):
    list_display = ["name", "is_published", "published_at", "created_at"]
    list_filter = ["is_published"]
    search_fields = ["name", "headline", "narrative"]
    prepopulated_fields = {"slug": ["name"]}
