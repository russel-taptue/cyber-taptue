import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView, View

from .forms import CustomAuthenticationForm, CustomUserCreationForm, OTPForm, ProfileForm
from .models import CustomUser, OTP, Profile

logger = logging.getLogger(__name__)


def _send_email(subject, context, html_template, txt_template, recipient):
    has_smtp = bool(settings.EMAIL_HOST_USER)
    has_sendgrid = hasattr(settings, "SENDGRID_API_KEY") and bool(settings.SENDGRID_API_KEY)
    if not has_smtp and not has_sendgrid:
        logger.warning("No email backend configured (EMAIL_HOST_USER or SENDGRID_API_KEY), skipping email")
        return
    try:
        html_message = render_to_string(html_template, context)
        plain_message = render_to_string(txt_template, context)
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
        )
    except Exception as exc:
        logger.warning("Failed to send email to %s: %s", recipient, exc)


def _send_otp_email(user, otp_code, request=None):
    _send_email(
        subject=_("Your login verification code"),
        context={"username": user.username, "otp_code": otp_code},
        html_template="accounts/emails/otp.html",
        txt_template="accounts/emails/otp.txt",
        recipient=user.email,
    )


def _send_welcome_email(user):
    login_url = settings.BASE_URL.rstrip("/") + reverse("accounts:login")
    _send_email(
        subject=_("Welcome to Cyber With Taptue!"),
        context={"username": user.username, "login_url": login_url},
        html_template="accounts/emails/welcome.html",
        txt_template="accounts/emails/welcome.txt",
        recipient=user.email,
    )


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        otp = OTP.create_and_invalidate_old(user)
        _send_otp_email(user, otp.code, request=self.request)
        self.request.session["_otp_user_id"] = user.pk
        messages.success(
            self.request,
            _("A verification code has been sent to your email."),
        )
        return redirect("accounts:verify_otp")


class VerifyOTPView(View):
    template_name = "accounts/verify_otp.html"
    form_class = OTPForm

    def dispatch(self, request, *args, **kwargs):
        if "_otp_user_id" not in request.session:
            messages.error(request, _("Please log in first."))
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        code = form.cleaned_data["code"]
        user_id = request.session["_otp_user_id"]
        user = get_object_or_404(CustomUser, pk=user_id)

        otp = OTP.objects.filter(user=user, is_used=False).first()

        if not otp:
            messages.error(request, _("No verification code found. Please request a new one."))
            return redirect("accounts:resend_otp")

        if otp.is_expired():
            messages.error(request, _("Verification code has expired. Please request a new one."))
            return redirect("accounts:resend_otp")

        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            if otp.is_max_attempts_reached():
                otp.is_used = True
                otp.save(update_fields=["is_used"])
                messages.error(
                    request,
                    _("Too many failed attempts. Please log in again to receive a new code."),
                )
                return redirect("accounts:login")
            messages.error(request, _("Incorrect verification code. Please try again."))
            return render(request, self.template_name, {"form": self.form_class()})

        otp.is_used = True
        otp.save(update_fields=["is_used"])
        del request.session["_otp_user_id"]
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, _("Welcome back, %(username)s!") % {"username": user.username})
        return redirect(settings.LOGIN_REDIRECT_URL)


class ResendOTPView(View):
    def dispatch(self, request, *args, **kwargs):
        if "_otp_user_id" not in request.session:
            messages.error(request, _("Please log in first."))
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        user_id = request.session["_otp_user_id"]
        user = get_object_or_404(CustomUser, pk=user_id)
        otp = OTP.create_and_invalidate_old(user)
        _send_otp_email(user, otp.code, request=request)
        messages.success(request, _("A new verification code has been sent to your email."))
        return redirect("accounts:verify_otp")


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")
    success_message = _("Account created successfully. You can now log in.")

    def form_valid(self, form):
        response = super().form_valid(form)
        _send_welcome_email(self.object)
        return response


class ProfileDetailView(DetailView):
    model = CustomUser
    template_name = "accounts/profile_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["profile"] = get_object_or_404(Profile, user=user)
        from apps.blog.models import Article
        from apps.projects.models import ProjectLab
        context["articles"] = Article.published.filter(author=user)[:6]
        context["projects"] = ProjectLab.published.filter(author=user)[:6]
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile_form.html"
    success_message = _("Profile updated successfully.")

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("accounts:profile_detail", kwargs={"username": self.request.user.username})
