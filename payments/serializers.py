from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    booking_event = serializers.CharField(source='booking.event.title', read_only=True)
    user_name     = serializers.CharField(source='booking.user.name', read_only=True)
    status        = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_event', 'user_name',
            'amount', 'phone_number', 'mpesa_code',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'mpesa_code', 'status', 'created_at',
            'updated_at', 'checkout_request_id'
        ]


class InitiatePaymentSerializer(serializers.Serializer):
    booking_id   = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
