from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Booking
from .serializers import BookingSerializer
from users.permissions import IsAdmin
from events.models import EventWaitlist


class CreateBookingView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')


class UserBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')


class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        if booking.status == 'cancelled':
            return Response({'error': 'Booking already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'cancelled'
        booking.save()

        # Notify next person on waitlist
        waitlist_entry = EventWaitlist.objects.filter(
            event=booking.event, notified=False
        ).order_by('joined_at').first()

        if waitlist_entry:
            waitlist_entry.notified = True
            waitlist_entry.save()
            # Notification will be handled by notifications app

        return Response({'message': 'Booking cancelled successfully'})


class OrganizerBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            event__organizer=self.request.user
        ).order_by('-booking_date')


class AdminBookingListView(generics.ListAPIView):
    queryset = Booking.objects.all().order_by('-booking_date')
    serializer_class = BookingSerializer
    permission_classes = [IsAdmin]


class ConfirmBookingView(APIView):
    """Called automatically after successful payment"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)
        if booking.status == 'confirmed':
            return Response({'message': 'Already confirmed'})
        booking.status = 'confirmed'
        booking.save()
        return Response({'message': 'Booking confirmed'})