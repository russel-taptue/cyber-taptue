from django.db.models import Count
from django.views.generic import DetailView, ListView

from apps.blog.models import Category
from .models import ProjectLab


class ProjectListView(ListView):
    model = ProjectLab
    paginate_by = 12
    context_object_name = "projects"

    def get_queryset(self):
        qs = ProjectLab.published.select_related("category", "author").all()
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        difficulty = self.request.GET.get("difficulty")
        if difficulty in ("beginner", "intermediate", "advanced"):
            qs = qs.filter(difficulty=difficulty)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            project_count=Count("projects")
        ).all()
        context["current_category"] = self.request.GET.get("category", "")
        context["current_difficulty"] = self.request.GET.get("difficulty", "")
        context["difficulty_choices"] = ProjectLab.Difficulty.choices
        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["projects/includes/project_grid.html"]
        return ["projects/project_list.html"]


class ProjectDetailView(DetailView):
    model = ProjectLab
    context_object_name = "project"
    template_name = "projects/project_detail.html"

    def get_queryset(self):
        return ProjectLab.published.select_related("category", "author").all()
