from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

from .forms import NewsletterForm
from .models import NewsletterSubscriber


class ContactView(TemplateView):
    template_name = "contact/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterForm()
        return context

    def post(self, request, *args, **kwargs):
        form = NewsletterForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email, defaults={"is_active": True}
            )
            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=["is_active"])
            self._send_welcome_email(subscriber)
            if request.headers.get("HX-Request"):
                html = render_to_string("contact/partials/newsletter_success.html", request=request)
                return HttpResponse(html)
            return self.get(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            html = render_to_string("contact/partials/newsletter_form.html", {
                "newsletter_form": form,
            }, request=request)
            return HttpResponse(html, status=422)
        return self.get(request, *args, **kwargs)

    def _send_welcome_email(self, subscriber):
        has_smtp = bool(settings.EMAIL_HOST_USER)
        has_sendgrid = hasattr(settings, "SENDGRID_API_KEY") and bool(settings.SENDGRID_API_KEY)
        if not has_smtp and not has_sendgrid:
            return
        unsubscribe_url = f"{settings.BASE_URL}/contact/unsubscribe/{subscriber.id}/"
        html_message = render_to_string("contact/emails/welcome.html", {
            "email": subscriber.email,
            "unsubscribe_url": unsubscribe_url,
        })
        plain_message = render_to_string("contact/emails/welcome.txt", {
            "email": subscriber.email,
            "unsubscribe_url": unsubscribe_url,
        })
        try:
            send_mail(
                subject=_("Welcome to Cyber With Taptue!"),
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception:
            pass


class UnsubscribeView(View):
    def get(self, request, subscriber_id):
        subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
        subscriber.is_active = False
        subscriber.save(update_fields=["is_active"])
        html = render_to_string("contact/unsubscribed.html", request=request)
        return HttpResponse(html)
