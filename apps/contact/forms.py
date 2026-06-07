from django import forms
from django.utils.translation import gettext_lazy as _

from .models import NewsletterSubscriber


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "placeholder": _("your@email.com"),
            "class": "w-full px-4 py-3 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors",
            "required": True,
        }),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(_("This email is already subscribed."))
        return email
