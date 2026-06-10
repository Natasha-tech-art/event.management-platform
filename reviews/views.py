from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewSerializer
from events.models import Event
from bookings.models import Booking


class EventReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(event_id=self.kwargs['event_id'])


class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])

        # Check user attended the event
        attended = Booking.objects.filter(
            user=self.request.user,
            event=event,
            status='confirmed'
        ).exists()

        if not attended:
            raise Exception('You can only review events you attended')

        serializer.save(user=self.request.user, event=event)


class UpdateDeleteReviewView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)