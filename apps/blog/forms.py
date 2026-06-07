from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label=_("Your comment"),
        widget=forms.Textarea(attrs={
            "rows": 4,
            "placeholder": _("Share your thoughts..."),
            "class": "w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:ring-2 focus:ring-cyber-500/30 focus:border-cyber-500 outline-none transition-colors resize-y",
        }),
    )

    class Meta:
        model = Comment
        fields = ("content", "parent")
        widgets = {
            "parent": forms.HiddenInput(),
        }
