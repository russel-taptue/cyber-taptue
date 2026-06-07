from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Article, Bookmark, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "content", "is_approved")
    readonly_fields = ("created_at",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "is_published", "published_at")
    list_filter = ("is_published", "category", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category", "author")
    date_hierarchy = "published_at"
    inlines = [CommentInline]
    fieldsets = (
        (None, {
            "fields": ("title", "title_fr", "slug", "category", "author"),
        }),
        (_("Content"), {
            "fields": ("content", "content_fr", "excerpt", "excerpt_fr"),
        }),
        (_("Media"), {
            "fields": ("featured_image", "youtube_video_id"),
            "classes": ("collapse",),
        }),
        (_("Publication"), {
            "fields": ("is_published", "published_at", "reading_time"),
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "article", "parent", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "author__username", "article__title")
    actions = ["approve_comments"]
    raw_id_fields = ("parent",)

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = _("Approve selected comments")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("user__email", "article__title")
    date_hierarchy = "created_at"
