from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import gettext_lazy as _

from .models import Article


class BlogRssFeed(Feed):
    feed_type = Rss201rev2Feed
    title = "Cyber With Taptue — Blog"
    link = "/blog/"
    description = _("Technical articles and tutorials on cybersecurity.")

    def items(self):
        return Article.published.select_related("author", "category").all()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.content[:300]

    def item_link(self, item):
        return reverse("blog:article_detail", kwargs={"slug": item.slug})

    def item_author_name(self, item):
        if item.author:
            return item.author.username
        return "Cyber With Taptue"

    def item_pubdate(self, item):
        return item.published_at

    def item_categories(self, item):
        if item.category:
            return (item.category.name,)
        return ()
