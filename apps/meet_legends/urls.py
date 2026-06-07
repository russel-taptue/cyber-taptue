from django.urls import path

from .views import LegendListView

app_name = "meet_legends"

urlpatterns = [
    path("", LegendListView.as_view(), name="legend_list"),
]
