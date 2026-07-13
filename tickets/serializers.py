from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    event_title  = serializers.CharField(source='booking.event.title', read_only=True)
    event_date   = serializers.DateTimeField(source='booking.event.start_date', read_only=True)
    event_venue  = serializers.CharField(source='booking.event.venue', read_only=True)
    attendee     = serializers.CharField(source='booking.user.name', read_only=True)
    quantity     = serializers.IntegerField(source='booking.ticket_quantity', read_only=True)
    qr_code      = serializers.ImageField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_ref', 'qr_code', 'checked_in', 'checked_in_at',
            'event_title', 'event_date', 'event_venue', 'attendee', 'quantity'
        ]
        read_only_fields = fields