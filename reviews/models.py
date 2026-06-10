from django.db import models
from django.conf import settings
from events.models import Event


class Review(models.Model):
    event      = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating     = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.name} - {self.event.title} ({self.rating}★)"