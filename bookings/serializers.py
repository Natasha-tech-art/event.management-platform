from rest_framework import serializers
from .models import Booking
from events.models import Event


class BookingSerializer(serializers.ModelSerializer):
    event_title    = serializers.CharField(source='event.title', read_only=True)
    event_date     = serializers.DateTimeField(source='event.start_date', read_only=True)
    event_venue    = serializers.CharField(source='event.venue', read_only=True)
    user_name      = serializers.CharField(source='user.name', read_only=True)
    total_amount   = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_name', 'event', 'event_title',
            'event_date', 'event_venue', 'ticket_quantity',
            'total_amount', 'booking_date', 'status', 'payment_ref'
        ]
        read_only_fields = ['user', 'total_amount', 'booking_date', 'status', 'payment_ref']

    def validate(self, data):
        event = data['event']
        quantity = data['ticket_quantity']

        if event.status != 'published':
            raise serializers.ValidationError('This event is not available for booking.')

        if event.remaining_tickets < quantity:
            raise serializers.ValidationError(
                f'Only {event.remaining_tickets} tickets remaining.'
            )
        return data