from django.contrib import admin
from .models import Event, Category, EventWaitlist

admin.site.register(Event)
admin.site.register(Category)
admin.site.register(EventWaitlist)
