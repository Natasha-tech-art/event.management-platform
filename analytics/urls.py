from django.urls import path
from .views import OrganizerAnalyticsView, AdminAnalyticsView, EventAnalyticsView

urlpatterns = [
    path('organizer/', OrganizerAnalyticsView.as_view(), name='organizer-analytics'),
    path('admin/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('event/<int:event_id>/', EventAnalyticsView.as_view(), name='event-analytics'),
]