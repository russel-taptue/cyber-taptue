from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import activate

from apps.contact.models import NewsletterSubscriber
from apps.contact.forms import NewsletterForm


class NewsletterSubscriberModelTest(TestCase):
    def test_create_subscriber(self):
        sub = NewsletterSubscriber.objects.create(email="test@example.com")
        self.assertEqual(sub.email, "test@example.com")
        self.assertTrue(sub.is_active)

    def test_email_unique(self):
        NewsletterSubscriber.objects.create(email="dup@example.com")
        with self.assertRaises(Exception):
            NewsletterSubscriber.objects.create(email="dup@example.com")

    def test_str_returns_email(self):
        sub = NewsletterSubscriber.objects.create(email="show@example.com")
        self.assertEqual(str(sub), "show@example.com")

    def test_default_is_active(self):
        sub = NewsletterSubscriber.objects.create(email="active@example.com")
        self.assertTrue(sub.is_active)

    def test_ordering(self):
        s1 = NewsletterSubscriber.objects.create(email="first@example.com")
        s2 = NewsletterSubscriber.objects.create(email="second@example.com")
        qs = NewsletterSubscriber.objects.all()
        self.assertEqual(qs.first(), s2)

    def test_unsubscribe_sets_inactive(self):
        sub = NewsletterSubscriber.objects.create(email="unsub@example.com")
        url = reverse("contact:unsubscribe", args=[sub.id])
        self.client.get(url)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)

    def test_unsubscribe_unknown_id_returns_404(self):
        url = reverse("contact:unsubscribe", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class NewsletterFormTest(TestCase):
    def setUp(self):
        activate("en")

    def test_valid_email(self):
        form = NewsletterForm(data={"email": "user@example.com"})
        self.assertTrue(form.is_valid())

    def test_blank_email(self):
        form = NewsletterForm(data={"email": ""})
        self.assertFalse(form.is_valid())

    def test_invalid_email_format(self):
        form = NewsletterForm(data={"email": "not-an-email"})
        self.assertFalse(form.is_valid())

    def test_duplicate_email(self):
        NewsletterSubscriber.objects.create(email="dup@example.com")
        form = NewsletterForm(data={"email": "dup@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("already subscribed", form.errors.get("email", [""])[0].lower())

    def test_duplicate_inactive_allows_resubscribe(self):
        NewsletterSubscriber.objects.create(email="prev@example.com", is_active=False)
        form = NewsletterForm(data={"email": "prev@example.com"})
        self.assertTrue(form.is_valid())

    def test_field_placeholder(self):
        form = NewsletterForm()
        self.assertEqual(form.fields["email"].widget.attrs["placeholder"], "your@email.com")


class ContactViewTest(TestCase):
    def setUp(self):
        activate("en")
        self.url = reverse("contact:contact")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact/contact.html")

    @override_settings(EMAIL_HOST_USER="")
    def test_post_valid_email_via_htmx(self):
        response = self.client.post(
            self.url, {"email": "newsub@example.com"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(NewsletterSubscriber.objects.filter(email="newsub@example.com").exists())

    def test_post_duplicate_email_via_htmx(self):
        NewsletterSubscriber.objects.create(email="existing@example.com")
        response = self.client.post(
            self.url, {"email": "existing@example.com"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 422)

    def test_post_invalid_email_via_htmx(self):
        response = self.client.post(
            self.url, {"email": "invalid"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 422)

    def test_non_htmx_post_returns_full_page(self):
        response = self.client.post(self.url, {"email": "fullpage@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact/contact.html")

    @override_settings(EMAIL_HOST_USER="test@gmail.com")
    def test_welcome_email_sent_on_subscribe(self):
        from django.core import mail
        mail.outbox = []
        response = self.client.post(
            self.url, {"email": "welcome@example.com"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome", mail.outbox[0].subject)
        self.assertIn("welcome@example.com", mail.outbox[0].to)
        self.assertIn("unsubscribe", mail.outbox[0].body.lower())
