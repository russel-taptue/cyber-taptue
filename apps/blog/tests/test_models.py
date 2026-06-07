from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.blog.models import Category, Article, Comment

User = get_user_model()


class CategoryModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(
            name="Network Security",
            name_fr="Sécurité Réseau",
            slug="network-security",
            description="Network security articles",
        )

    def test_str(self):
        self.assertEqual(str(self.cat), "Network Security")

    def test_bilingual_fields(self):
        self.assertEqual(self.cat.name_fr, "Sécurité Réseau")

    def test_default_order(self):
        cat2 = Category.objects.create(name="AAA", slug="aaa", order=0)
        qs = Category.objects.all()
        self.assertEqual(qs.first(), cat2)

    def test_slug_unique(self):
        with self.assertRaises(Exception):
            Category.objects.create(name="Other", slug="network-security")


class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="author@example.com", username="author", password="p1"
        )
        self.cat = Category.objects.create(name="Cloud", slug="cloud")
        self.article = Article.objects.create(
            title="Debian 12 Hardening",
            title_fr="Durcissement Debian 12",
            slug="debian-12-hardening",
            category=self.cat,
            author=self.user,
            content="# Step 1\nInstall the OS.",
            content_fr="# Étape 1\nInstaller le système.",
            excerpt="A hardening guide",
            reading_time=15,
            is_published=True,
            published_at=timezone.now(),
        )

    def test_str(self):
        self.assertEqual(str(self.article), "Debian 12 Hardening")

    def test_published_manager(self):
        self.assertIn(self.article, Article.published.all())

    def test_unpublished_excluded(self):
        draft = Article.objects.create(
            title="Draft",
            slug="draft",
            author=self.user,
            content="Draft content",
            is_published=False,
        )
        self.assertNotIn(draft, Article.published.all())

    def test_future_published_excluded(self):
        future = Article.objects.create(
            title="Future",
            slug="future",
            author=self.user,
            content="Future content",
            is_published=True,
            published_at=timezone.now() + timezone.timedelta(days=7),
        )
        self.assertNotIn(future, Article.published.all())

    def test_auto_publish_on_save(self):
        article = Article.objects.create(
            title="Auto Pub", slug="auto-pub", author=self.user,
            content="x", is_published=True, published_at=None,
        )
        article.refresh_from_db()
        self.assertIsNotNone(article.published_at)

    def test_bilingual_content(self):
        self.assertEqual(self.article.title_fr, "Durcissement Debian 12")
        self.assertEqual(self.article.content_fr, "# Étape 1\nInstaller le système.")

    def test_ordering(self):
        older = Article.objects.create(
            title="Older", slug="older", author=self.user, content="x",
            is_published=True, published_at=timezone.now() - timezone.timedelta(days=1),
        )
        qs = Article.published.all()
        self.assertEqual(qs.first(), self.article)
        self.assertEqual(qs.last(), older)

    def test_category_relation(self):
        self.assertEqual(self.article.category, self.cat)
        self.assertIn(self.article, self.cat.articles.all())

    def test_slug_unique(self):
        with self.assertRaises(Exception):
            Article.objects.create(title="Same Slug", slug="debian-12-hardening", author=self.user, content="x")


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="commenter@example.com", username="commenter", password="p1"
        )
        self.article = Article.objects.create(
            title="Test", slug="test", author=self.user, content="x",
            is_published=True, published_at=timezone.now(),
        )
        self.comment = Comment.objects.create(
            article=self.article, author=self.user, content="Great article!",
        )

    def test_str(self):
        self.assertIn(self.article.title, str(self.comment))
        self.assertIn(self.user.username, str(self.comment))

    def test_approved_by_default(self):
        self.assertTrue(self.comment.is_approved)

    def test_ordering(self):
        c2 = Comment.objects.create(
            article=self.article, author=self.user, content="Second!",
        )
        qs = Comment.objects.all()
        self.assertEqual(qs.first(), self.comment)
        self.assertEqual(qs.last(), c2)

    def test_article_relation(self):
        self.assertIn(self.comment, self.article.comments.all())
