from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from events.models import Event
from bookings.models import Booking
from tickets.models import Ticket
from users.models import User
from payments.models import Payment
from users.permissions import IsAdmin, IsOrganizer


class OrganizerAnalyticsView(APIView):
    permission_classes = [IsOrganizer]

    def get(self, request):
        events = Event.objects.filter(organizer=request.user)
        total_events    = events.count()
        published       = events.filter(status='published').count()
        total_bookings  = Booking.objects.filter(event__organizer=request.user, status='confirmed').count()
        total_revenue   = Payment.objects.filter(
            booking__event__organizer=request.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Monthly ticket sales (database-agnostic — works on SQLite, Postgres, etc.)
        monthly_sales_qs = Booking.objects.filter(
            event__organizer=request.user,
            status='confirmed'
        ).annotate(month=TruncMonth('booking_date')).values('month').annotate(
            total=Count('id')
        ).order_by('month')

        monthly_sales = [
            {'month': entry['month'].strftime('%m'), 'total': entry['total']}
            for entry in monthly_sales_qs if entry['month'] is not None
        ]

        return Response({
            'total_events': total_events,
            'published_events': published,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'monthly_sales': monthly_sales,
        })


class AdminAnalyticsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        total_users   = User.objects.count()
        total_events  = Event.objects.count()
        total_bookings = Booking.objects.filter(status='confirmed').count()
        total_revenue  = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            'total_users': total_users,
            'total_events': total_events,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
        })


class EventAnalyticsView(APIView):
    permission_classes = [IsOrganizer]

    def get(self, request, event_id):
        event          = Event.objects.get(pk=event_id, organizer=request.user)
        total_tickets  = event.capacity
        booked         = Booking.objects.filter(event=event, status='confirmed').aggregate(
            total=Sum('ticket_quantity')
        )['total'] or 0
        checked_in     = Ticket.objects.filter(
            booking__event=event, checked_in=True
        ).count()
        revenue        = Payment.objects.filter(
            booking__event=event, status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'event': event.title,
            'total_capacity': total_tickets,
            'tickets_booked': booked,
            'tickets_remaining': total_tickets - booked,
            'checked_in': checked_in,
            'revenue': revenue,
            'occupancy_rate': f"{(booked/total_tickets*100):.1f}%" if total_tickets > 0 else "0%"
        })