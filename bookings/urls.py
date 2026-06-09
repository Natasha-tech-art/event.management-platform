from django.urls import path
from .views import (
    CreateBookingView, UserBookingListView, BookingDetailView,
    CancelBookingView, OrganizerBookingListView,
    AdminBookingListView, ConfirmBookingView
)

urlpatterns = [
    path('', UserBookingListView.as_view(), name='my-bookings'),
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('<int:pk>/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('organizer/', OrganizerBookingListView.as_view(), name='organizer-bookings'),
    path('admin/all/', AdminBookingListView.as_view(), name='admin-bookings'),
]