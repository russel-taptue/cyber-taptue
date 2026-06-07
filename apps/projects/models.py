from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            published_at__lte=timezone.now(),
        )


class ProjectLab(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")

    title = models.CharField(_("title"), max_length=255)
    title_fr = models.CharField(_("title (French)"), max_length=255, blank=True)
    slug = models.SlugField(_("slug"), max_length=280, unique=True)
    category = models.ForeignKey(
        "blog.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name=_("category"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name=_("author"),
    )
    summary = models.TextField(_("summary"), max_length=500)
    summary_fr = models.TextField(_("summary (French)"), max_length=500, blank=True)
    content = models.TextField(_("content (Markdown)"))
    content_fr = models.TextField(_("content (French, Markdown)"), blank=True)
    skills_acquired = models.TextField(_("skills acquired"), blank=True,
        help_text=_("Comma-separated list of skills"))
    skills_acquired_fr = models.TextField(_("skills acquired (French)"), blank=True)
    github_url = models.URLField(_("GitHub URL"), max_length=500, blank=True)
    youtube_video_id = models.CharField(_("YouTube video ID"), max_length=50, blank=True)
    difficulty = models.CharField(
        _("difficulty"),
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    featured_image = models.ImageField(_("featured image"), upload_to="projects/", blank=True)

    is_published = models.BooleanField(_("is published"), default=False)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = _("Project / Lab")
        verbose_name_plural = _("Projects / Labs")
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
