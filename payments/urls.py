from django.urls import path
from .views import (
    InitiatePaymentView, MpesaCallbackView,
    PaymentStatusView, AdminPaymentListView
)

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('status/<int:booking_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('admin/all/', AdminPaymentListView.as_view(), name='admin-payments'),
]