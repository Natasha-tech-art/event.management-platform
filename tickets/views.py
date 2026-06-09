from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Ticket
from .serializers import TicketSerializer
from .utils import generate_qr_code, notify_ticket_update
from bookings.models import Booking
from users.permissions import IsStaff, IsAdmin
import uuid


class GenerateTicketView(APIView):
    """Generate ticket after booking is confirmed"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

        if booking.status != 'confirmed':
            return Response(
                {'error': 'Booking must be confirmed before generating a ticket'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if ticket already exists
        if hasattr(booking, 'ticket'):
            serializer = TicketSerializer(booking.ticket)
            return Response(serializer.data)

        # Create ticket
        ticket = Ticket(booking=booking)
        ticket.ticket_ref = f"EVT-{booking.event.id}-{uuid.uuid4().hex[:8].upper()}"
        ticket = generate_qr_code(ticket)
        ticket.save()

        # Notify real-time ticket update
        notify_ticket_update(booking.event.id, booking.event.remaining_tickets)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyTicketsView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            booking__user=self.request.user,
            booking__status='confirmed'
        )


class TicketDetailView(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(booking__user=self.request.user)


class CheckInTicketView(APIView):
    """Staff scans QR code and checks in attendee"""
    permission_classes = [IsStaff]

    def post(self, request):
        ticket_ref = request.data.get('ticket_ref')

        if not ticket_ref:
            return Response({'error': 'ticket_ref is required'}, status=status.HTTP_400_BAD_REQUEST)

        ticket = get_object_or_404(Ticket, ticket_ref=ticket_ref)

        if ticket.checked_in:
            return Response({
                'error': 'Ticket already used',
                'checked_in_at': ticket.checked_in_at
            }, status=status.HTTP_400_BAD_REQUEST)

        if ticket.booking.event.status not in ['published', 'completed']:
            return Response({'error': 'Event is not active'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.checked_in = True
        ticket.checked_in_at = timezone.now()
        ticket.save()

        return Response({
            'message': 'Check-in successful',
            'attendee': ticket.booking.user.name,
            'event': ticket.booking.event.title,
            'checked_in_at': ticket.checked_in_at
        })


class EventAttendanceView(APIView):
    """Staff views attendance stats for an event"""
    permission_classes = [IsStaff]

    def get(self, request, event_id):
        tickets = Ticket.objects.filter(booking__event__id=event_id)
        total     = tickets.count()
        checked   = tickets.filter(checked_in=True).count()
        remaining = total - checked

        return Response({
            'event_id': event_id,
            'total_tickets': total,
            'checked_in': checked,
            'not_checked_in': remaining,
            'attendance_rate': f"{(checked/total*100):.1f}%" if total > 0 else "0%"
        })


class AdminTicketListView(generics.ListAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdmin]