from django.urls import path
from .views import (
    CategoryListCreateView, EventListView, EventCreateView,
    EventDetailView, EventUpdateView, EventDeleteView,
    OrganizerEventListView, PublishEventView, CancelEventView,
    JoinWaitlistView, AdminEventListView, AdminApproveEventView
)

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('create/', EventCreateView.as_view(), name='event-create'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('<int:pk>/update/', EventUpdateView.as_view(), name='event-update'),
    path('<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),
    path('<int:pk>/publish/', PublishEventView.as_view(), name='event-publish'),
    path('<int:pk>/cancel/', CancelEventView.as_view(), name='event-cancel'),
    path('<int:pk>/waitlist/', JoinWaitlistView.as_view(), name='event-waitlist'),
    path('my-events/', OrganizerEventListView.as_view(), name='my-events'),
    path('categories/', CategoryListCreateView.as_view(), name='categories'),
    path('admin/all/', AdminEventListView.as_view(), name='admin-events'),
    path('admin/<int:pk>/approve/', AdminApproveEventView.as_view(), name='admin-approve-event'),
]