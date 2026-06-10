from django.urls import path
from .views import EventReviewListView, CreateReviewView, UpdateDeleteReviewView

urlpatterns = [
    path('event/<int:event_id>/', EventReviewListView.as_view(), name='event-reviews'),
    path('event/<int:event_id>/create/', CreateReviewView.as_view(), name='create-review'),
    path('<int:pk>/', UpdateDeleteReviewView.as_view(), name='review-detail'),
]