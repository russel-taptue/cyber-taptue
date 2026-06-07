from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from apps.contact.models import NewsletterSubscriber


class Command(BaseCommand):
    help = "Send a newsletter email to all active subscribers"

    def add_arguments(self, parser):
        parser.add_argument("subject", type=str, help="Email subject")
        parser.add_argument(
            "--template",
            type=str,
            default="contact/emails/newsletter.html",
            help="HTML template path (default: contact/emails/newsletter.html)",
        )
        parser.add_argument(
            "--text-template",
            type=str,
            default="contact/emails/newsletter.txt",
            help="Plain text template path (default: contact/emails/newsletter.txt)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print recipient count without sending",
        )

    def handle(self, *args, **options):
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        count = subscribers.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("No active subscribers to send to"))
            return

        if options["dry_run"]:
            self.stdout.write(f"Would send to {count} subscriber(s)")
            return

        subject = options["subject"]
        html_template = options["template"]
        text_template = options["text_template"]
        unsubscribe_base = f"{settings.BASE_URL}/contact/unsubscribe/"

        sent = 0
        failed = 0
        for subscriber in subscribers:
            context = {
                "email": subscriber.email,
                "unsubscribe_url": f"{unsubscribe_base}{subscriber.id}/",
                "year": timezone.now().year,
            }
            try:
                html_message = render_to_string(html_template, context)
                plain_message = render_to_string(text_template, context)
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                sent += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to send to {subscriber.email}: {e}"))
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"Sent to {sent} subscriber(s)"))
        if failed:
            self.stdout.write(self.style.WARNING(f"Failed: {failed}"))
