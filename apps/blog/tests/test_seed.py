from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model

from apps.blog.models import Category, Article
from apps.projects.models import ProjectLab
from apps.events.models import Event
from apps.meet_legends.models import Legend

User = get_user_model()


class SeedPlatformCommandTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command("seed_platform", stdout=out)
        output = out.getvalue()
        self.assertIn("Seeding Cyber With Taptue", output)
        self.assertIn("taptuerussel@gmail.com", output)
        self.assertIn("articles", output)
        self.assertIn("project labs", output)
        self.assertIn("events", output)
        self.assertIn("legends", output)

    def test_creates_founder(self):
        call_command("seed_platform", stdout=StringIO())
        self.assertTrue(User.objects.filter(email="taptuerussel@gmail.com").exists())

    def test_founder_is_superuser(self):
        call_command("seed_platform", stdout=StringIO())
        user = User.objects.get(email="taptuerussel@gmail.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_creates_all_categories(self):
        call_command("seed_platform", stdout=StringIO())
        self.assertEqual(Category.objects.count(), 4)
        for slug in ("cloud-security", "web-security", "network-security", "osint"):
            self.assertTrue(Category.objects.filter(slug=slug).exists())

    def test_creates_all_articles(self):
        call_command("seed_platform", stdout=StringIO())
        self.assertEqual(Article.objects.count(), 4)
        for slug in ("debian-12-bookworm-server-installation", "owasp-top-10-2025-guide",
                     "wireshark-network-forensics", "osint-investigation-techniques"):
            self.assertTrue(Article.objects.filter(slug=slug).exists())

    def test_article_has_markdown_content(self):
        call_command("seed_platform", stdout=StringIO())
        article = Article.objects.get(slug="debian-12-bookworm-server-installation")
        self.assertIn("nftables", article.content)
        self.assertIn("fail2ban", article.content)

    def test_article_has_french_content(self):
        call_command("seed_platform", stdout=StringIO())
        article = Article.objects.get(slug="debian-12-bookworm-server-installation")
        self.assertTrue(len(article.content_fr) > 50)

    def test_article_has_github_url(self):
        call_command("seed_platform", stdout=StringIO())
        article = Article.objects.get(slug="debian-12-bookworm-server-installation")
        self.assertIn("github.com/russel-taptue", article.content)

    def test_creates_all_projects(self):
        call_command("seed_platform", stdout=StringIO())
        self.assertEqual(ProjectLab.objects.count(), 3)
        for slug in ("deploy-hardened-web-server", "sql-injection-lab", "pcap-analysis-challenge"):
            self.assertTrue(ProjectLab.objects.filter(slug=slug).exists())

    def test_creates_all_events(self):
        call_command("seed_platform", stdout=StringIO())
        self.assertEqual(Event.objects.count(), 2)
        for slug in ("cybershow-2026", "zero-day-workshop-2026"):
            self.assertTrue(Event.objects.filter(slug=slug).exists())

    def test_creates_all_legends(self):
        call_command("seed_platform", stdout=StringIO())
        self.assertEqual(Legend.objects.count(), 3)
        for slug in ("kevin-mitnick", "eva-galperin", "mikko-hypponen"):
            self.assertTrue(Legend.objects.filter(slug=slug).exists())

    def test_idempotent(self):
        out1 = StringIO()
        out2 = StringIO()
        call_command("seed_platform", stdout=out1)
        call_command("seed_platform", stdout=out2)
        self.assertIn("exists, skipping", out2.getvalue())
        self.assertEqual(Article.objects.count(), 4)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(ProjectLab.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Legend.objects.count(), 3)
        self.assertEqual(User.objects.filter(email="taptuerussel@gmail.com").count(), 1)
