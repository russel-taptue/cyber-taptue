from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.blog.models import Category, Article, Comment

User = get_user_model()


class ArticleListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            email="author@example.com", username="author", password="p1"
        )
        cat = Category.objects.create(name="Cloud", slug="cloud")
        for i in range(12):
            Article.objects.create(
                title=f"Article {i}", slug=f"article-{i}",
                author=user, category=cat, content="x",
                is_published=True, published_at=timezone.now(),
            )
        cls.url = reverse("blog:article_list")

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/article_list.html")

    def test_pagination_12_per_page(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["articles"]), 12)

    def test_page_2_out_of_range_returns_404(self):
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, 404)

    def test_category_filter(self):
        cat2 = Category.objects.create(name="Network", slug="network")
        Article.objects.create(
            title="Net Article", slug="net-1", author=User.objects.first(),
            category=cat2, content="x", is_published=True, published_at=timezone.now(),
        )
        response = self.client.get(self.url + "?domain=network")
        self.assertEqual(len(response.context["articles"]), 1)
        self.assertEqual(response.context["articles"][0].slug, "net-1")

    def test_htmx_returns_partial(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "blog/includes/article_grid.html")

    def test_empty_state(self):
        Article.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "htmx-indicator")

    def test_category_filter_htmx(self):
        response = self.client.get(
            self.url + "?domain=nonexistent", HTTP_HX_REQUEST="true"
        )
        self.assertTemplateUsed(response, "blog/includes/article_grid.html")


class ArticleDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Tutorials", slug="tutorials")
        user = User.objects.create_user(
            email="author@example.com", username="author", password="p1"
        )
        cls.article = Article.objects.create(
            title="Deep Dive", slug="deep-dive", author=user,
            category=cls.cat, content="# Title\nContent with `code`.",
            is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("blog:article_detail", kwargs={"slug": "deep-dive"})

    def test_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/article_detail.html")

    def test_404_for_missing(self):
        url = reverse("blog:article_detail", kwargs={"slug": "nonexistent"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_context_contains_article(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["article"], self.article)

    def test_markdown_rendered(self):
        response = self.client.get(self.url)
        self.assertContains(response, "<h1>")
        self.assertContains(response, "Title")

    def test_related_articles_same_category(self):
        related = Article.objects.create(
            title="Related Post", slug="related-post", author=User.objects.first(),
            category=self.cat, content="x", is_published=True, published_at=timezone.now(),
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Related Post")

    def test_related_articles_different_category_excluded(self):
        other_cat = Category.objects.create(name="Other", slug="other")
        Article.objects.create(
            title="Unrelated", slug="unrelated", author=User.objects.first(),
            category=other_cat, content="x", is_published=True, published_at=timezone.now(),
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, "Unrelated")

    def test_related_articles_omits_current_article(self):
        related = Article.objects.create(
            title="Another Tutorial", slug="another", author=User.objects.first(),
            category=self.cat, content="x", is_published=True, published_at=timezone.now(),
        )
        response = self.client.get(self.url)
        self.assertNotIn(self.article, response.context["related_articles"])
        self.assertIn(related, response.context["related_articles"])

    def test_unpublished_returns_404(self):
        draft = Article.objects.create(
            title="Draft", slug="draft", author=User.objects.first(),
            content="x", is_published=False,
        )
        url = reverse("blog:article_detail", kwargs={"slug": "draft"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_share_buttons_rendered(self):
        response = self.client.get(self.url)
        self.assertContains(response, "twitter.com/intent/tweet")
        self.assertContains(response, "linkedin.com/shareArticle")
        self.assertContains(response, "facebook.com/sharer")
        self.assertContains(response, "navigator.clipboard.writeText")

    def test_og_meta_tags_present(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'og:title')
        self.assertContains(response, 'og:description')
        self.assertContains(response, 'og:type')
        self.assertContains(response, 'og:url')
        self.assertContains(response, 'og:image')

    def test_og_title_matches_article(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'og:title" content="Deep Dive')

    def test_og_type_is_article(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'og:type" content="article')


class ArticleCommentPostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="commenter@example.com", username="commenter", password="p1"
        )
        cls.article = Article.objects.create(
            title="Discuss", slug="discuss", author=cls.user,
            content="x", is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("blog:article_comment", kwargs={"slug": "discuss"})

    def test_post_requires_login(self):
        response = self.client.post(self.url, {"content": "Nice!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.comments.count(), 0)

    def test_authenticated_user_can_comment(self):
        self.client.login(email="commenter@example.com", password="p1")
        response = self.client.post(self.url, {"content": "Great post!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.comments.count(), 1)

    def test_empty_content_rejected(self):
        self.client.login(email="commenter@example.com", password="p1")
        initial_count = self.article.comments.count()
        response = self.client.post(self.url, {"content": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.comments.count(), initial_count)

    def test_htmx_post_returns_partial(self):
        self.client.login(email="commenter@example.com", password="p1")
        response = self.client.post(
            self.url, {"content": "HTMX comment"}, HTTP_HX_REQUEST="true"
        )
        self.assertTemplateUsed(response, "blog/includes/comment_list.html")


class CommentReplyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com", username="user", password="p1"
        )
        cls.article = Article.objects.create(
            title="Discuss", slug="discuss", author=cls.user,
            content="x", is_published=True, published_at=timezone.now(),
        )
        cls.parent = Comment.objects.create(
            article=cls.article, author=cls.user, content="Parent comment",
        )
        cls.post_url = reverse("blog:article_comment", kwargs={"slug": "discuss"})
        cls.form_url = reverse("blog:reply_form", kwargs={"slug": "discuss", "parent_id": cls.parent.pk})

    def test_reply_form_requires_login(self):
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 400)

    def test_reply_form_200_when_logged_in(self):
        self.client.login(email="user@example.com", password="p1")
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/includes/reply_form.html")

    def test_reply_creates_nested_comment(self):
        self.client.login(email="user@example.com", password="p1")
        response = self.client.post(self.post_url, {
            "content": "A reply",
            "parent": self.parent.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parent.replies.count(), 1)
        self.assertEqual(self.parent.replies.first().content, "A reply")

    def test_reply_appears_in_comment_list(self):
        self.client.login(email="user@example.com", password="p1")
        reply = Comment.objects.create(
            article=self.article, author=self.user,
            content="Nested reply", parent=self.parent,
        )
        detail_url = reverse("blog:article_detail", kwargs={"slug": "discuss"})
        response = self.client.get(detail_url)
        self.assertIn(self.parent, response.context["comments"])
        self.assertIn(reply, self.parent.replies.all())

    def test_top_level_comments_exclude_replies(self):
        reply = Comment.objects.create(
            article=self.article, author=self.user,
            content="Nested", parent=self.parent,
        )
        detail_url = reverse("blog:article_detail", kwargs={"slug": "discuss"})
        response = self.client.get(detail_url)
        self.assertIn(self.parent, response.context["comments"])
        self.assertNotIn(reply, response.context["comments"])


class BookmarkViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com", username="user", password="p1"
        )
        cat = Category.objects.create(name="Cloud", slug="cloud")
        cls.article = Article.objects.create(
            title="Test Article", slug="test-article",
            author=cls.user, category=cat, content="x",
            is_published=True, published_at=timezone.now(),
        )
        cls.toggle_url = reverse("blog:toggle_bookmark", kwargs={"slug": cls.article.slug})
        cls.list_url = reverse("blog:bookmark_list")

    def test_toggle_adds_bookmark(self):
        self.client.login(email="user@example.com", password="p1")
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.bookmarks.count(), 1)

    def test_toggle_removes_bookmark(self):
        self.client.login(email="user@example.com", password="p1")
        self.client.post(self.toggle_url)
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.bookmarks.count(), 0)

    def test_toggle_unauthenticated_returns_400(self):
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 400)

    def test_toggle_returns_bookmark_button_partial(self):
        self.client.login(email="user@example.com", password="p1")
        response = self.client.post(self.toggle_url)
        self.assertTemplateUsed(response, "blog/includes/bookmark_button.html")

    def test_bookmark_list_requires_login(self):
        response = self.client.get(self.list_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.list_url}")

    def test_bookmark_list_shows_bookmarked_articles(self):
        self.client.login(email="user@example.com", password="p1")
        self.client.post(self.toggle_url)
        response = self.client.get(self.list_url)
        self.assertContains(response, "Test Article")

    def test_bookmark_list_empty(self):
        self.client.login(email="user@example.com", password="p1")
        response = self.client.get(self.list_url)
        self.assertContains(response, "Pas encore de favoris.")

    def test_article_detail_shows_bookmarked_context(self):
        self.client.login(email="user@example.com", password="p1")
        response = self.client.get(
            reverse("blog:article_detail", kwargs={"slug": self.article.slug})
        )
        self.assertIn("bookmarked", response.context)
        self.assertFalse(response.context["bookmarked"])


class RssFeedTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            email="author@example.com", username="author", password="p1"
        )
        cat = Category.objects.create(name="Tutorials", slug="tutorials")
        cls.article = Article.objects.create(
            title="Test Article", slug="test-article", author=user,
            category=cat, content="Full content here.", excerpt="Short excerpt.",
            is_published=True, published_at=timezone.now(),
        )
        cls.url = reverse("blog:rss_feed")

    def test_rss_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_rss_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(response["Content-Type"], "application/rss+xml; charset=utf-8")

    def test_rss_contains_article_title(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Test Article")

    def test_rss_contains_article_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, "test-article")

    def test_rss_contains_article_description(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Short excerpt.")

    def test_rss_does_not_include_unpublished(self):
        Article.objects.create(
            title="Draft", slug="draft", author=User.objects.first(),
            content="x", is_published=False,
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, "Draft")

    def test_rss_feed_title(self):
        response = self.client.get(self.url)
        self.assertContains(response, "<title>Cyber With Taptue")

    def test_rss_author_present(self):
        response = self.client.get(self.url)
        self.assertContains(response, "author")

    def test_rss_category_present(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Tutorials")
