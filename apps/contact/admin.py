from django.contrib import admin

from apps.contact.models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "date_subscribed", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["email"]
    date_hierarchy = "date_subscribed"
