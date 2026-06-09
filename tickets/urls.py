from django.urls import path
from .views import (
    GenerateTicketView, MyTicketsView, TicketDetailView,
    CheckInTicketView, EventAttendanceView, AdminTicketListView
)

urlpatterns = [
    path('', MyTicketsView.as_view(), name='my-tickets'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('generate/<int:booking_id>/', GenerateTicketView.as_view(), name='generate-ticket'),
    path('checkin/', CheckInTicketView.as_view(), name='checkin-ticket'),
    path('attendance/<int:event_id>/', EventAttendanceView.as_view(), name='event-attendance'),
    path('admin/all/', AdminTicketListView.as_view(), name='admin-tickets'),
]