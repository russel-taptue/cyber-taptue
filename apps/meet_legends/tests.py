from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from apps.meet_legends.models import Legend


class LegendModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.legend = Legend.objects.create(
            name="John Doe",
            headline="From Engineer to CISO",
            headline_fr="D'Ingénieur à RSSI",
            narrative="John started as an electrical engineer...",
            narrative_fr="John a commencé comme ingénieur électrique...",
            youtube_video_id="abc123xyz",
            slug="john-doe",
            is_published=True,
            published_at=timezone.now(),
        )

    def test_str(self):
        self.assertEqual(str(self.legend), "John Doe")

    def test_published_manager(self):
        self.assertIn(self.legend, Legend.published.all())

    def test_unpublished_excluded(self):
        draft = Legend.objects.create(
            name="Draft", slug="draft-l", youtube_video_id="x", is_published=False,
        )
        self.assertNotIn(draft, Legend.published.all())

    def test_bilingual_fields(self):
        self.assertEqual(self.legend.headline_fr, "D'Ingénieur à RSSI")
        self.assertEqual(self.legend.narrative_fr, "John a commencé comme ingénieur électrique...")

    def test_slug_unique(self):
        with self.assertRaises(Exception):
            Legend.objects.create(
                name="Other", slug="john-doe", youtube_video_id="y",
            )

    def test_youtube_id_required(self):
        legend = Legend.objects.create(
            name="Video Required", slug="video-req", youtube_video_id="vid123",
            is_published=True, published_at=timezone.now(),
        )
        self.assertEqual(legend.youtube_video_id, "vid123")


class LegendListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Legend.objects.create(
            name="Alice", slug="alice", youtube_video_id="a1",
            is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("meet_legends:legend_list")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/legends.html")

    def test_shows_legends(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Alice")

    def test_empty_state(self):
        Legend.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "No legends yet")

    def test_unpublished_not_shown(self):
        Legend.objects.create(
            name="Hidden", slug="hidden", youtube_video_id="h1", is_published=False,
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, "Hidden")
