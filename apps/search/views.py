from django.db import connection
from django.db.models import Q, Value
from django.shortcuts import render
from django.utils.translation import get_language
from django.views.generic import TemplateView

from apps.blog.models import Article
from apps.projects.models import ProjectLab


def _backend():
    return connection.vendor


def _is_pg():
    return _backend() == "postgresql"


def _search_articles(query):
    if _is_pg():
        from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
        vector = SearchVector("title", "title_fr", "content", "content_fr", "excerpt", "excerpt_fr")
        sq = SearchQuery(query)
        return (
            Article.published.annotate(rank=SearchRank(vector, sq))
            .filter(rank__gte=0.01)
            .order_by("-rank")
        )
    q = Q(title__icontains=query) | Q(title_fr__icontains=query)
    q |= Q(content__icontains=query) | Q(content_fr__icontains=query)
    q |= Q(excerpt__icontains=query) | Q(excerpt_fr__icontains=query)
    return Article.published.filter(q)


def _search_projects(query):
    if _is_pg():
        from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
        vector = SearchVector(
            "title", "title_fr",
            "summary", "summary_fr",
            "content", "content_fr",
            "skills_acquired", "skills_acquired_fr",
        )
        sq = SearchQuery(query)
        return (
            ProjectLab.published.annotate(rank=SearchRank(vector, sq))
            .filter(rank__gte=0.01)
            .order_by("-rank")
        )
    q = Q(title__icontains=query) | Q(title_fr__icontains=query)
    q |= Q(summary__icontains=query) | Q(summary_fr__icontains=query)
    q |= Q(content__icontains=query) | Q(content_fr__icontains=query)
    q |= Q(skills_acquired__icontains=query) | Q(skills_acquired_fr__icontains=query)
    return ProjectLab.published.filter(q)


class SearchView(TemplateView):
    template_name = "search/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query

        if query:
            context["articles"] = _search_articles(query)[:10]
            context["projects"] = _search_projects(query)[:10]
            context["total"] = context["articles"].count() + context["projects"].count()

        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["search/includes/results_partial.html"]
        return ["search/results.html"]
