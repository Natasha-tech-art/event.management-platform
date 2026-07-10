from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking
from events.models import Category, Event
from payments.models import Payment
from users.models import User


class PaymentStatusViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Music')
        self.event = Event.objects.create(
            organizer=self.user,
            title='Sample Event',
            description='A sample event',
            category=self.category,
            venue='Hall A',
            location='Nairobi',
            start_date=timezone.now(),
            end_date=timezone.now(),
            ticket_price='100.00',
            capacity=100,
            status='published'
        )

    def test_payment_status_view_keeps_pending_status_for_pending_payment(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            ticket_quantity=1,
            total_amount=0
        )
        Payment.objects.create(
            booking=booking,
            amount='100.00',
            phone_number='0712345678',
            status='pending'
        )

        response = self.client.get(f'/api/payments/status/{booking.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['payment']['status'], 'pending')
        self.assertEqual(response.json()['booking_status'], 'pending')

    def test_payment_status_view_keeps_failed_status_for_failed_payment(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            ticket_quantity=1,
            total_amount=0
        )
        booking.status = 'confirmed'
        booking.save(update_fields=['status'])
        Payment.objects.create(
            booking=booking,
            amount='100.00',
            phone_number='0712345678',
            status='failed'
        )

        response = self.client.get(f'/api/payments/status/{booking.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['payment']['status'], 'failed')
        self.assertEqual(response.json()['booking_status'], 'confirmed')

    def test_payment_status_view_returns_completed_for_completed_payment(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            ticket_quantity=1,
            total_amount=0
        )
        booking.status = 'confirmed'
        booking.save(update_fields=['status'])
        Payment.objects.create(
            booking=booking,
            amount='100.00',
            phone_number='0712345678',
            status='completed',
            mpesa_code='ABC123'
        )

        response = self.client.get(f'/api/payments/status/{booking.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['payment']['status'], 'completed')
        self.assertEqual(response.json()['booking_status'], 'confirmed')
