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


class Legend(models.Model):
    name = models.CharField(_("expert name"), max_length=200)
    headline = models.CharField(_("headline"), max_length=300, help_text=_("EN portfolio title"))
    headline_fr = models.CharField(_("headline (French)"), max_length=300, blank=True, help_text=_("FR portfolio title"))
    narrative = models.TextField(_("narrative"), help_text=_("EN career-pivot / milestone story"))
    narrative_fr = models.TextField(_("narrative (French)"), blank=True, help_text=_("FR career-pivot / milestone story"))
    youtube_video_id = models.CharField(_("YouTube video ID"), max_length=50, help_text=_("Valid channel stream key"))
    slug = models.SlugField(_("slug"), max_length=280, unique=True)
    featured_image = models.ImageField(_("featured image"), upload_to="legends/", blank=True)

    is_published = models.BooleanField(_("is published"), default=False)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = _("Legend")
        verbose_name_plural = _("Legends")
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
