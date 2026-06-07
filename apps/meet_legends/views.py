from django.views.generic import ListView

from .models import Legend


class LegendListView(ListView):
    model = Legend
    queryset = Legend.published.all()
    context_object_name = "legends"
    template_name = "pages/legends.html"
