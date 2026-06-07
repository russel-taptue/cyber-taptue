from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    name_fr = models.CharField(_("name (French)"), max_length=100, blank=True)
    slug = models.SlugField(_("slug"), max_length=120, unique=True)
    description = models.TextField(_("description"), blank=True)
    description_fr = models.TextField(_("description (French)"), blank=True)
    icon = models.CharField(_("icon"), max_length=50, blank=True, help_text=_("Tailwind icon or emoji"))
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            published_at__lte=timezone.now(),
        )


class Article(models.Model):
    title = models.CharField(_("title"), max_length=255)
    title_fr = models.CharField(_("title (French)"), max_length=255, blank=True)
    slug = models.SlugField(_("slug"), max_length=280, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name=_("category"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name=_("author"),
    )
    content = models.TextField(_("content (Markdown)"))
    content_fr = models.TextField(_("content (French, Markdown)"), blank=True)
    excerpt = models.TextField(_("excerpt"), blank=True, max_length=500)
    excerpt_fr = models.TextField(_("excerpt (French)"), blank=True, max_length=500)
    featured_image = models.ImageField(_("featured image"), upload_to="blog/", blank=True)
    youtube_video_id = models.CharField(_("YouTube video ID"), max_length=50, blank=True)
    reading_time = models.PositiveIntegerField(_("reading time (minutes)"), default=5)

    is_published = models.BooleanField(_("is published"), default=False)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("article"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("author"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("parent comment"),
    )
    content = models.TextField(_("content"), max_length=2000)
    is_approved = models.BooleanField(_("is approved"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} — {self.article.title[:50]}"


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
        verbose_name=_("user"),
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="bookmarks",
        verbose_name=_("article"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Bookmark")
        verbose_name_plural = _("Bookmarks")
        unique_together = ("user", "article")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} :: {self.article.title[:50]}"
