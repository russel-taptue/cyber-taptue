from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.blog.forms import CommentForm

User = get_user_model()


class CommentFormTest(TestCase):
    def test_valid_data(self):
        form = CommentForm(data={"content": "Great article!"})
        self.assertTrue(form.is_valid())

    def test_blank_content(self):
        form = CommentForm(data={"content": ""})
        self.assertFalse(form.is_valid())

    def test_whitespace_content(self):
        form = CommentForm(data={"content": "   "})
        self.assertFalse(form.is_valid())

    def test_max_length_not_enforced_by_form(self):
        form = CommentForm(data={"content": "x" * 2001})
        self.assertTrue(form.is_valid())

    def test_content_field_label(self):
        form = CommentForm()
        self.assertEqual(form.fields["content"].label, "Your comment")

    def test_content_field_widget_placeholder(self):
        form = CommentForm()
        self.assertEqual(form.fields["content"].widget.attrs["placeholder"], "Share your thoughts...")

    def test_widget_has_tailwind_class(self):
        form = CommentForm()
        self.assertIn("w-full", form.fields["content"].widget.attrs.get("class", ""))
