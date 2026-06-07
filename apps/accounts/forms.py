from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Profile


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={
            "autofocus": True,
            "placeholder": _("you@example.com"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            "autofocus": True,
            "placeholder": _("Enter your new password"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Repeat your new password"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )


class OTPForm(forms.Form):
    code = forms.CharField(
        label=_("Verification code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "autofocus": True,
            "autocomplete": "one-time-code",
            "inputmode": "numeric",
            "class": "w-full text-center text-2xl tracking-[0.5em] font-mono rounded-lg border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
            "placeholder": "000000",
        }),
    )

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not code.isdigit():
            raise forms.ValidationError(_("Verification code must contain only digits."))
        return code


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={
            "autofocus": True,
            "placeholder": _("you@example.com"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            "placeholder": _("Choose a username"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Create a strong password"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Repeat your password"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "username")


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={
            "autofocus": True,
            "placeholder": _("you@example.com"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Enter your password"),
            "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
        }),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", "bio", "website", "github", "linkedin", "twitter")
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors resize-y",
                "placeholder": _("Tell us about yourself..."),
            }),
            "website": forms.URLInput(attrs={
                "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
                "placeholder": "https://example.com",
            }),
            "github": forms.URLInput(attrs={
                "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
                "placeholder": "https://github.com/username",
            }),
            "linkedin": forms.URLInput(attrs={
                "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
                "placeholder": "https://linkedin.com/in/username",
            }),
            "twitter": forms.URLInput(attrs={
                "class": "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
                "placeholder": "https://twitter.com/username",
            }),
        }
