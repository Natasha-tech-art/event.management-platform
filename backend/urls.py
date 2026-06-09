from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="EventHub API",
        default_version='v1',
        description="Event Management Platform API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/events/', include('events.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/payments/', include('payments.urls')),
    # Swagger docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
