from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.utils.translation import gettext_lazy as _

from .forms import CommentForm
from .models import Article, Bookmark, Category, Comment


class ArticleListView(ListView):
    model = Article
    paginate_by = 12
    context_object_name = "articles"

    def get_queryset(self):
        qs = Article.published.select_related("category", "author").all()
        domain_slug = self.request.GET.get("domain")
        if domain_slug:
            qs = qs.filter(category__slug=domain_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            article_count=Count("articles")
        ).all()
        context["current_domain"] = self.request.GET.get("domain", "")
        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["blog/includes/article_grid.html"]
        return ["blog/article_list.html"]


class ArticleDetailView(DetailView):
    model = Article
    context_object_name = "article"
    template_name = "blog/article_detail.html"

    def get_queryset(self):
        return Article.published.select_related(
            "category", "author"
        ).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        article = self.object
        context["comments"] = article.comments.filter(
            is_approved=True, parent__isnull=True
        ).select_related("author").prefetch_related(
            "replies__author"
        )
        if article.category:
            context["related_articles"] = Article.published.filter(
                category=article.category
            ).exclude(pk=article.pk)[:3]
        else:
            context["related_articles"] = Article.published.exclude(
                pk=article.pk
            )[:3]
        if self.request.user.is_authenticated:
            context["bookmarked"] = Bookmark.objects.filter(
                user=self.request.user, article=article
            ).exists()
        return context


def article_comment_post(request, slug):
    article = get_object_or_404(Article.published, slug=slug)
    form = CommentForm(data=request.POST)
    if form.is_valid() and request.user.is_authenticated:
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.save()
    comments = article.comments.filter(is_approved=True, parent__isnull=True).select_related("author").prefetch_related(
        "replies__author"
    )
    html = render_to_string("blog/includes/comment_list.html", {
        "comments": comments,
        "article": article,
        "comment_form": form if not form.is_valid() else None,
    }, request=request)
    return HttpResponse(html)


def reply_form(request, slug, parent_id):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    article = get_object_or_404(Article.published, slug=slug)
    parent = get_object_or_404(Comment, pk=parent_id, article=article, is_approved=True)
    form = CommentForm(initial={"parent": parent})
    html = render_to_string("blog/includes/reply_form.html", {
        "form": form,
        "article": article,
        "parent": parent,
    }, request=request)
    return HttpResponse(html)


@require_POST
def toggle_bookmark(request, slug):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    article = get_object_or_404(Article.published, slug=slug)
    bookmark = Bookmark.objects.filter(user=request.user, article=article)
    if bookmark.exists():
        bookmark.delete()
        bookmarked = False
    else:
        Bookmark.objects.create(user=request.user, article=article)
        bookmarked = True
    html = render_to_string("blog/includes/bookmark_button.html", {
        "article": article,
        "bookmarked": bookmarked,
    }, request=request)
    return HttpResponse(html)


class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = "blog/bookmark_list.html"
    context_object_name = "bookmarks"
    paginate_by = 12

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user,
            article__is_published=True,
        ).select_related("article", "article__category").order_by("-created_at")
