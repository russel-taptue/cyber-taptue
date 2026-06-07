import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="customuser_set",
        related_query_name="customuser",
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
    )
    avatar = models.ImageField(
        _("avatar"), upload_to="avatars/", blank=True,
    )
    bio = models.TextField(_("bio"), blank=True, max_length=500)
    website = models.URLField(_("website"), blank=True, max_length=300)
    github = models.URLField(_("GitHub"), blank=True, max_length=300)
    linkedin = models.URLField(_("LinkedIn"), blank=True, max_length=300)
    twitter = models.URLField(_("Twitter"), blank=True, max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("accounts:profile_detail", kwargs={"username": self.user.username})

    @property
    def contribution_count(self):
        from apps.blog.models import Article
        from apps.projects.models import ProjectLab
        articles = Article.objects.filter(author=self.user).count()
        projects = ProjectLab.objects.filter(author=self.user).count()
        return articles + projects


class OTP(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="otps",
        verbose_name=_("user"),
    )
    code = models.CharField(_("code"), max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(_("is used"), default=False)
    attempts = models.PositiveSmallIntegerField(_("attempts"), default=0)

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.email}"

    def is_expired(self):
        from django.conf import settings
        expiry = settings.OTP_EXPIRY_MINUTES
        return timezone.now() > self.created_at + timezone.timedelta(minutes=expiry)

    def is_max_attempts_reached(self):
        from django.conf import settings
        return self.attempts >= settings.OTP_MAX_ATTEMPTS

    @staticmethod
    def generate_code():
        return "".join(random.choices(string.digits, k=6))

    @staticmethod
    def create_and_invalidate_old(user):
        OTP.objects.filter(user=user, is_used=False).update(is_used=True)
        code = OTP.generate_code()
        return OTP.objects.create(user=user, code=code)
