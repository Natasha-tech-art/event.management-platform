from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    organizer    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title        = models.CharField(max_length=255)
    description  = models.TextField()
    category     = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    venue        = models.CharField(max_length=255)
    location     = models.CharField(max_length=255)
    start_date   = models.DateTimeField()
    end_date     = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    capacity     = models.PositiveIntegerField()
    banner       = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def remaining_tickets(self):
        booked = self.bookings.filter(status='confirmed').aggregate(
            total=models.Sum('ticket_quantity')
        )['total'] or 0
        return self.capacity - booked

    @property
    def is_full(self):
        return self.remaining_tickets <= 0


class EventWaitlist(models.Model):
    event     = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waitlist')
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    notified  = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.name} waiting for {self.event.title}"