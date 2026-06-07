from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.blog.models import Category
from apps.projects.models import ProjectLab

User = get_user_model()


class ProjectLabModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="author@a.com", username="author", password="p")
        cls.cat = Category.objects.create(name="Cloud", slug="cloud")
        cls.project = ProjectLab.objects.create(
            title="Build a SIEM Lab",
            title_fr="Construire un lab SIEM",
            slug="build-siem-lab",
            category=cls.cat,
            author=cls.user,
            summary="Learn to build a SIEM",
            content="## Steps\n\n1. Install",
            content_fr="## Étapes\n\n1. Installer",
            skills_acquired="Elasticsearch, Kibana, Fleet",
            github_url="https://github.com/russel-taptue/siem-lab",
            difficulty="intermediate",
            is_published=True,
            published_at=timezone.now(),
        )

    def test_str(self):
        self.assertEqual(str(self.project), "Build a SIEM Lab")

    def test_published_manager(self):
        self.assertIn(self.project, ProjectLab.published.all())

    def test_unpublished_excluded(self):
        draft = ProjectLab.objects.create(
            title="Draft", slug="draft-p", author=self.user, content="x", is_published=False,
        )
        self.assertNotIn(draft, ProjectLab.published.all())

    def test_difficulty_choices(self):
        self.assertIn(self.project.difficulty, dict(ProjectLab.Difficulty.choices))

    def test_skills_list(self):
        skills = self.project.skills_acquired.split(",")
        self.assertEqual(len(skills), 3)

    def test_github_url_present(self):
        self.assertTrue(self.project.github_url.startswith("https://github.com"))

    def test_bilingual_fields(self):
        self.assertEqual(self.project.title_fr, "Construire un lab SIEM")
        self.assertEqual(self.project.content_fr, "## Étapes\n\n1. Installer")

    def test_difficulty_default(self):
        p = ProjectLab.objects.create(title="Default", slug="default", author=self.user, content="x")
        self.assertEqual(p.difficulty, "beginner")


class ProjectListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email="a@a.com", username="a", password="p")
        cat = Category.objects.create(name="Cloud", slug="cloud")
        for i in range(10):
            diffs = ["beginner", "intermediate", "advanced"]
            ProjectLab.objects.create(
                title=f"Project {i}", slug=f"project-{i}", author=user,
                category=cat, content="x", is_published=True, published_at=timezone.now(),
                difficulty=diffs[i % 3],
            )
        cls.url = reverse("projects:project_list")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_pagination_returns_all_when_under_limit(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["projects"]), 10)

    def test_htmx_returns_partial(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "projects/includes/project_grid.html")

    def test_empty_state(self):
        ProjectLab.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["projects"]), 0)

    def test_filter_by_difficulty_beginner(self):
        response = self.client.get(self.url, {"difficulty": "beginner"})
        self.assertEqual(len(response.context["projects"]), 4)

    def test_filter_by_difficulty_intermediate(self):
        response = self.client.get(self.url, {"difficulty": "intermediate"})
        self.assertEqual(len(response.context["projects"]), 3)

    def test_filter_by_difficulty_advanced(self):
        response = self.client.get(self.url, {"difficulty": "advanced"})
        self.assertEqual(len(response.context["projects"]), 3)

    def test_filter_by_invalid_difficulty_returns_all(self):
        response = self.client.get(self.url, {"difficulty": "expert"})
        self.assertEqual(len(response.context["projects"]), 10)

    def test_filter_by_category_and_difficulty(self):
        response = self.client.get(self.url, {"category": "cloud", "difficulty": "beginner"})
        self.assertEqual(len(response.context["projects"]), 4)

    def test_difficulty_choices_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("difficulty_choices", response.context)
        self.assertEqual(len(response.context["difficulty_choices"]), 3)

    def test_current_difficulty_in_context(self):
        response = self.client.get(self.url, {"difficulty": "advanced"})
        self.assertEqual(response.context["current_difficulty"], "advanced")


class ProjectDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email="a@a.com", username="a", password="p")
        cls.project = ProjectLab.objects.create(
            title="Deep Lab", slug="deep-lab", author=user,
            content="# Guide\nSteps here.", is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("projects:project_detail", kwargs={"slug": "deep-lab"})

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_404_for_missing(self):
        url = reverse("projects:project_detail", kwargs={"slug": "nope"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_markdown_rendered(self):
        response = self.client.get(self.url)
        self.assertContains(response, "<h1>")
