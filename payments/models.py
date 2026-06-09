from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    booking         = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number    = models.CharField(max_length=15)
    mpesa_code      = models.CharField(max_length=50, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.mpesa_code} - {self.status}"