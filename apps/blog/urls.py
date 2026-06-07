from django.urls import path

from . import views
from .feeds import BlogRssFeed

app_name = "blog"

urlpatterns = [
    path("feed/rss/", BlogRssFeed(), name="rss_feed"),
    path("", views.ArticleListView.as_view(), name="article_list"),
    path("bookmarks/", views.BookmarkListView.as_view(), name="bookmark_list"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("<slug:slug>/comment/", views.article_comment_post, name="article_comment"),
    path("<slug:slug>/comment/<int:parent_id>/reply/", views.reply_form, name="reply_form"),
    path("<slug:slug>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
]
