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


class Event(models.Model):
    title = models.CharField(_("title"), max_length=255)
    title_fr = models.CharField(_("title (French)"), max_length=255, blank=True)
    slug = models.SlugField(_("slug"), max_length=280, unique=True)
    venue = models.CharField(_("venue"), max_length=300)
    venue_fr = models.CharField(_("venue (French)"), max_length=300, blank=True)
    patronage = models.CharField(_("patronage"), max_length=300, blank=True, help_text=_("Official patronage / auspices"))
    patronage_fr = models.CharField(_("patronage (French)"), max_length=300, blank=True)
    start_date = models.DateTimeField(_("start date"))
    end_date = models.DateTimeField(_("end date"))
    summary = models.TextField(_("summary"), max_length=500)
    summary_fr = models.TextField(_("summary (French)"), max_length=500, blank=True)
    content = models.TextField(_("content (Markdown)"), help_text=_("Full event recap in Markdown"))
    content_fr = models.TextField(_("content (French, Markdown)"), blank=True)
    youtube_video_id = models.CharField(_("YouTube video ID"), max_length=50, blank=True)
    photo_gallery = models.JSONField(_("photo gallery"), blank=True, default=list, help_text=_("Array of image paths"))
    featured_image = models.ImageField(_("featured image"), upload_to="events/", blank=True)

    is_published = models.BooleanField(_("is published"), default=False)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
