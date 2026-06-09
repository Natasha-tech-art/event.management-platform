from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Event, Category, EventWaitlist
from .serializers import EventSerializer, CategorySerializer, EventWaitlistSerializer
from users.permissions import IsOrganizer, IsAdmin


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdmin()]


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'venue', 'location']
    ordering_fields = ['start_date', 'ticket_price', 'created_at']

    def get_queryset(self):
        queryset = Event.objects.filter(status='published')
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')
        date     = self.request.query_params.get('date')
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if date:
            queryset = queryset.filter(start_date__date=date)
        return queryset


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]


class EventUpdateView(generics.UpdateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


class EventDeleteView(generics.DestroyAPIView):
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


class OrganizerEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


class PublishEventView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user)
        event.status = 'published'
        event.save()
        return Response({'message': 'Event published successfully'})


class CancelEventView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user)
        event.status = 'cancelled'
        event.save()
        return Response({'message': 'Event cancelled'})


class JoinWaitlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not event.is_full:
            return Response({'message': 'Event still has tickets available'}, status=status.HTTP_400_BAD_REQUEST)
        waitlist, created = EventWaitlist.objects.get_or_create(event=event, user=request.user)
        if created:
            return Response({'message': 'Added to waitlist'})
        return Response({'message': 'Already on waitlist'})


class AdminEventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdmin]


class AdminApproveEventView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.status = 'published'
        event.save()
        return Response({'message': 'Event approved and published'})