from rest_framework import serializers
from .models import Event, Category, EventWaitlist


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    organizer_name     = serializers.CharField(source='organizer.name', read_only=True)
    category_name      = serializers.CharField(source='category.name', read_only=True)
    remaining_tickets  = serializers.ReadOnlyField()
    is_full            = serializers.ReadOnlyField()
    price              = serializers.DecimalField(source='ticket_price', max_digits=10, decimal_places=2, write_only=True, required=False)
    banner             = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'organizer_name', 'title', 'description',
            'category', 'category_name', 'venue', 'location',
            'start_date', 'end_date', 'ticket_price', 'price', 'capacity',
            'banner', 'status', 'remaining_tickets', 'is_full',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']


class EventWaitlistSerializer(serializers.ModelSerializer):
    user_name  = serializers.CharField(source='user.name', read_only=True)
    event_name = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventWaitlist
        fields = ['id', 'event', 'event_name', 'user', 'user_name', 'joined_at', 'notified']
        read_only_fields = ['user', 'joined_at', 'notified']