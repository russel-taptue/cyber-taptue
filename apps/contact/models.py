from django.db import models
from django.utils.translation import gettext_lazy as _


class NewsletterSubscriber(models.Model):
    email = models.EmailField(_("email"), unique=True)
    date_subscribed = models.DateTimeField(_("date subscribed"), auto_now_add=True)
    is_active = models.BooleanField(_("is active"), default=True)

    class Meta:
        verbose_name = _("Newsletter subscriber")
        verbose_name_plural = _("Newsletter subscribers")
        ordering = ["-date_subscribed"]

    def __str__(self):
        return self.email
