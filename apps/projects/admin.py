from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ProjectLab


@admin.register(ProjectLab)
class ProjectLabAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "difficulty", "is_published", "published_at")
    list_filter = ("is_published", "difficulty", "category")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category", "author")
    date_hierarchy = "published_at"
    fieldsets = (
        (None, {
            "fields": ("title", "title_fr", "slug", "category", "author", "difficulty"),
        }),
        (_("Content"), {
            "fields": ("summary", "summary_fr", "content", "content_fr", "skills_acquired", "skills_acquired_fr"),
        }),
        (_("Links & Media"), {
            "fields": ("github_url", "youtube_video_id", "featured_image"),
        }),
        (_("Publication"), {
            "fields": ("is_published", "published_at"),
        }),
    )
