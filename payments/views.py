from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer, InitiatePaymentSerializer
from .mpesa import stk_push
from bookings.models import Booking
from users.permissions import IsAdmin


class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        booking_id   = serializer.validated_data['booking_id']
        phone_number = serializer.validated_data.get('phone_number') or request.user.phone_number
        booking      = get_object_or_404(Booking, pk=booking_id, user=request.user)

        if not phone_number:
            return Response(
                {'error': 'Phone number is required to initiate payment.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == 'confirmed':
            return Response({'error': 'Booking already paid'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data.get('phone_number') and request.user.phone_number != phone_number:
            request.user.phone_number = phone_number
            request.user.save(update_fields=['phone_number'])

        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_amount,
                'phone_number': phone_number,
                'status': 'pending'
            }
        )

        if not created and payment.phone_number != phone_number:
            payment.phone_number = phone_number
            payment.save(update_fields=['phone_number'])

        response = stk_push(phone_number, booking.total_amount, booking.id)

        if response.get('ResponseCode') == '0':
            payment.checkout_request_id = response.get('CheckoutRequestID')
            payment.merchant_request_id = response.get('MerchantRequestID')
            payment.save()
            return Response({
                'message': 'Payment initiated. Check your phone for the M-Pesa prompt.',
                'checkout_request_id': payment.checkout_request_id,
                'status': payment.status
            })

        return Response({
            'error': 'Failed to initiate payment',
            'details': response
        }, status=status.HTTP_400_BAD_REQUEST)


class MpesaCallbackView(APIView):
    """Safaricom calls this URL after payment"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data     = request.data
        callback = data.get('Body', {}).get('stkCallback', {})
        result_code = callback.get('ResultCode')
        checkout_id = callback.get('CheckoutRequestID')

        payment = Payment.objects.filter(checkout_request_id=checkout_id).first()
        if not payment:
            merchant_id = callback.get('MerchantRequestID')
            payment = Payment.objects.filter(merchant_request_id=merchant_id).first()

        if not payment:
            return Response({'message': 'Payment not found'})

        if result_code == 0:
            # Payment successful
            items = callback.get('CallbackMetadata', {}).get('Item', [])
            mpesa_code = next(
                (i['Value'] for i in items if i.get('Name') == 'MpesaReceiptNumber'), None
            )
            payment.status = 'completed'
            if mpesa_code:
                payment.mpesa_code = mpesa_code
            payment.save()

            # Confirm the booking automatically
            booking = payment.booking
            booking.status = 'confirmed'
            if mpesa_code:
                booking.payment_ref = mpesa_code
            booking.save()

        else:
            payment.status = 'failed'
            payment.save()

        return Response({'message': 'Callback received'})


class PaymentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
        payment = get_object_or_404(Payment, booking=booking)

        if payment.status == 'pending' and booking.status == 'confirmed':
            if payment.mpesa_code or booking.payment_ref:
                payment.status = 'completed'
                if booking.payment_ref and not payment.mpesa_code:
                    payment.mpesa_code = booking.payment_ref
                payment.save(update_fields=['status', 'mpesa_code'])

        serializer = PaymentSerializer(payment)
        return Response({
            'payment': serializer.data,
            'booking_status': booking.status
        })


class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]