from django.db import models
from bookings.models import Booking
import uuid


class Ticket(models.Model):
    booking    = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    ticket_ref = models.CharField(max_length=50, unique=True)
    qr_code    = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket {self.ticket_ref}"

    def generate_ticket_ref(self):
        return f"EVT-{self.booking.event.id}-{uuid.uuid4().hex[:8].upper()}"