from django.views.generic import DetailView, ListView

from .models import Event


class EventListView(ListView):
    model = Event
    queryset = Event.published.all()
    context_object_name = "events"
    template_name = "events/event_list.html"


class EventDetailView(DetailView):
    model = Event
    queryset = Event.published.all()
    context_object_name = "event"
    template_name = "events/event_detail.html"
