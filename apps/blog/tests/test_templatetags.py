from django.test import TestCase
from django.template import Template, Context
from django.utils.translation import activate

from apps.blog.templatetags.markdown_extras import render_markdown, translated_field, split, trim
from apps.blog.models import Article
from django.contrib.auth import get_user_model

User = get_user_model()


class RenderMarkdownFilterTest(TestCase):
    def test_converts_markdown_to_html(self):
        result = render_markdown("# Title\n\nParagraph.")
        self.assertIn("<h1>", result)
        self.assertIn("Title", result)
        self.assertIn("<p>", result)
        self.assertIn("Paragraph.", result)

    def test_sanitizes_script_tags(self):
        result = render_markdown("<script>alert('xss')</script>")
        self.assertNotIn("<script>", result)

    def test_renders_code_blocks(self):
        result = render_markdown("```python\nprint('hello')\n```")
        self.assertIn("<code", result)
        self.assertIn("print", result)

    def test_renders_tables(self):
        result = render_markdown("| A | B |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<table>", result)
        self.assertIn("<td>", result)

    def test_allows_safe_tags(self):
        result = render_markdown('<strong>Bold</strong> and <em>italic</em>')
        self.assertIn("<strong>", result)
        self.assertIn("<em>", result)

    def test_strips_forbidden_tags(self):
        result = render_markdown('<iframe src="x"></iframe><style>.x{}</style>')
        self.assertNotIn("<iframe>", result)
        self.assertNotIn("<style>", result)


class TranslatedFieldFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email="a@a.com", username="a", password="p")
        cls.article = Article.objects.create(
            title="English Title", title_fr="Titre Français",
            slug="test", author=user, content="x",
        )

    def test_returns_english_when_active_is_en(self):
        activate("en")
        result = translated_field(self.article, "title")
        self.assertEqual(result, "English Title")

    def test_returns_french_when_active_is_fr(self):
        activate("fr")
        result = translated_field(self.article, "title")
        self.assertEqual(result, "Titre Français")

    def test_falls_back_to_english_when_fr_empty(self):
        activate("fr")
        self.article.title_fr = ""
        result = translated_field(self.article, "title")
        self.assertEqual(result, "English Title")

    def test_works_in_template(self):
        activate("fr")
        t = Template("{% load markdown_extras %}{{ a|translated_field:'title' }}")
        c = Context({"a": self.article})
        result = t.render(c)
        self.assertEqual(result, "Titre Français")


class SplitFilterTest(TestCase):
    def test_splits_by_comma(self):
        result = split("a, b, c")
        self.assertEqual(result, ["a", "b", "c"])

    def test_splits_by_custom_sep(self):
        result = split("a|b|c", "|")
        self.assertEqual(result, ["a", "b", "c"])

    def test_returns_list(self):
        result = split("")
        self.assertIsInstance(result, list)

    def test_single_item(self):
        result = split("only")
        self.assertEqual(result, ["only"])


class TrimFilterTest(TestCase):
    def test_trims_whitespace(self):
        self.assertEqual(trim("  hello  "), "hello")

    def test_trims_newlines(self):
        self.assertEqual(trim("\nhello\n"), "hello")

    def test_no_change_for_clean(self):
        self.assertEqual(trim("hello"), "hello")

    def test_empty_string(self):
        self.assertEqual(trim(""), "")
