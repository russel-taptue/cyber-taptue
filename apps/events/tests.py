from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from apps.events.models import Event


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(
            title="CyberShow 2026",
            title_fr="CyberShow 2026",
            slug="cybershow-2026",
            venue="Palais des Congrès, Paris",
            venue_fr="Palais des Congrès, Paris",
            start_date=timezone.now() - timezone.timedelta(days=30),
            end_date=timezone.now() - timezone.timedelta(days=28),
            summary="A major cybersecurity event",
            content="## Recap\n\nGreat conference!",
            photo_gallery=["images/events/cybershow_1.jpg", "images/events/cybershow_2.jpg"],
            is_published=True,
            published_at=timezone.now(),
        )

    def test_str(self):
        self.assertEqual(str(self.event), "CyberShow 2026")

    def test_published_manager(self):
        self.assertIn(self.event, Event.published.all())

    def test_unpublished_excluded(self):
        draft = Event.objects.create(
            title="Draft", slug="draft-e", start_date=timezone.now(), end_date=timezone.now(),
            content="x", is_published=False,
        )
        self.assertNotIn(draft, Event.published.all())

    def test_photo_gallery_json(self):
        self.assertEqual(len(self.event.photo_gallery), 2)
        self.assertIn("cybershow_1.jpg", self.event.photo_gallery[0])

    def test_bilingual_fields(self):
        self.assertEqual(self.event.venue, "Palais des Congrès, Paris")

    def test_ordering_by_start_date(self):
        older = Event.objects.create(
            title="Older", slug="older", start_date=timezone.now() - timezone.timedelta(days=100),
            end_date=timezone.now() - timezone.timedelta(days=98), content="x",
            is_published=True, published_at=timezone.now(),
        )
        qs = Event.published.all()
        self.assertEqual(qs.first(), self.event)

    def test_patronage_optional(self):
        self.assertEqual(self.event.patronage, "")


class EventListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Event.objects.create(
            title="Test Event", slug="test-event",
            start_date=timezone.now(), end_date=timezone.now(),
            content="x", is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("events:event_list")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_shows_events(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Test Event")

    def test_empty_state(self):
        Event.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "No events yet")


class EventDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(
            title="Big Conference", slug="big-conf",
            start_date=timezone.now(), end_date=timezone.now(),
            content="## Great event", is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("events:event_detail", kwargs={"slug": "big-conf"})

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_404_for_missing(self):
        url = reverse("events:event_detail", kwargs={"slug": "nope"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
