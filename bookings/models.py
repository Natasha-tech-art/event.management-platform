from django.db import models
from django.conf import settings
from events.models import Event


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    event           = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    ticket_quantity = models.PositiveIntegerField(default=1)
    total_amount    = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date    = models.DateTimeField(auto_now_add=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_ref     = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.name} - {self.event.title} ({self.status})"

    def save(self, *args, **kwargs):
        self.total_amount = self.event.ticket_price * self.ticket_quantity
        super().save(*args, **kwargs)