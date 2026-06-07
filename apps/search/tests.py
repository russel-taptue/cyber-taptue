from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.blog.models import Article, Category
from apps.projects.models import ProjectLab

User = get_user_model()


@override_settings(LANGUAGE_CODE="en")
class SearchPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            email="author@example.com", username="author", password="p1"
        )
        cat = Category.objects.create(name="Cloud", slug="cloud")

        cls.article = Article.objects.create(
            title="Debian Server Security",
            slug="debian-security",
            author=user,
            category=cat,
            content="Hardening Debian 12 for production use.",
            excerpt="A guide to securing your Debian server.",
            is_published=True,
            published_at=timezone.now(),
        )
        cls.article_fr = Article.objects.create(
            title="Sécurité des serveurs Debian",
            slug="debian-securite",
            title_fr="Sécurité des serveurs Debian",
            author=user,
            category=cat,
            content_fr="Durcir Debian 12 pour la production.",
            is_published=True,
            published_at=timezone.now(),
        )
        cls.project = ProjectLab.objects.create(
            title="Kali Linux Lab Setup",
            slug="kali-lab",
            author=user,
            summary="Setting up a Kali Linux lab environment.",
            content="Step by step guide to Kali Linux.",
            is_published=True,
            published_at=timezone.now(),
        )

        cls.url = reverse("search:search")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search/results.html")

    def test_search_by_title(self):
        response = self.client.get(self.url, {"q": "Debian"})
        self.assertContains(response, "Debian Server Security")

    def test_search_by_content(self):
        response = self.client.get(self.url, {"q": "Hardening"})
        self.assertContains(response, "Debian Server Security")

    def test_search_by_excerpt(self):
        response = self.client.get(self.url, {"q": "securing"})
        self.assertContains(response, "Debian Server Security")

    def test_search_french_title(self):
        response = self.client.get(self.url, {"q": "Sécurité"})
        self.assertContains(response, "Sécurité des serveurs Debian")

    def test_search_french_content(self):
        response = self.client.get(self.url, {"q": "Durcir"})
        self.assertContains(response, "Sécurité des serveurs Debian")

    def test_search_projects(self):
        response = self.client.get(self.url, {"q": "Kali"})
        self.assertContains(response, "Kali Linux Lab Setup")

    def test_search_finds_both_articles_and_projects(self):
        response = self.client.get(self.url, {"q": "Debian"})
        self.assertContains(response, "Debian Server Security")
        self.assertNotContains(response, "Kali Linux Lab Setup")

    def test_no_results(self):
        response = self.client.get(self.url, {"q": "xyznonexistent"})
        self.assertContains(response, "No results found")

    def test_empty_query_returns_prompt(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Enter a search term above")

    def test_htmx_request_returns_partial(self):
        response = self.client.get(self.url + "?q=Debian", HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "search/includes/results_partial.html")

    def test_does_not_search_unpublished_articles(self):
        Article.objects.create(
            title="Secret Draft", slug="secret-draft", author=User.objects.first(),
            content="hidden", is_published=False,
        )
        response = self.client.get(self.url, {"q": "Secret"})
        self.assertNotContains(response, "Secret Draft")

    def test_does_not_search_unpublished_projects(self):
        ProjectLab.objects.create(
            title="Hidden Lab", slug="hidden-lab", author=User.objects.first(),
            summary="hidden", is_published=False,
        )
        response = self.client.get(self.url, {"q": "Hidden"})
        self.assertNotContains(response, "Hidden Lab")
