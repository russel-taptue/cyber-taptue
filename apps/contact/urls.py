from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    path("", views.ContactView.as_view(), name="contact"),
    path("unsubscribe/<int:subscriber_id>/", views.UnsubscribeView.as_view(), name="unsubscribe"),
]
