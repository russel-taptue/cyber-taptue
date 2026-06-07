from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "start_date", "end_date", "venue", "is_published"]
    list_filter = ["is_published", "start_date"]
    search_fields = ["title", "venue", "summary"]
    prepopulated_fields = {"slug": ["title"]}
    fieldsets = [
        ("Titles", {"fields": ["title", "title_fr", "slug"]}),
        ("Venue & Patronage", {"fields": ["venue", "venue_fr", "patronage", "patronage_fr"]}),
        ("Dates", {"fields": ["start_date", "end_date"]}),
        ("Content", {"fields": ["summary", "summary_fr", "content", "content_fr"]}),
        ("Media", {"fields": ["youtube_video_id", "photo_gallery", "featured_image"]}),
        ("Publication", {"fields": ["is_published", "published_at"]}),
    ]
