# EventHub – Event Management & Ticketing Platform (Backend)

A full-featured REST API backend for a complete Event Management and Ticketing Platform built with Django and Django REST Framework. The system supports event creation, ticket booking, QR code generation, M-Pesa payments, real-time updates, analytics, and role-based access control.

---

## Project Overview

**EventHub** is a multi-user event management and ticketing platform similar to Eventbrite or Ticketmaster. It allows:

- **Event Organizers** to create, manage, and analyze events
- **Attendees** to discover, book, and attend events
- **Staff** to verify attendees using QR code scanning
- **Admins** to oversee the entire platform

---

## API Modules

### 1. Users Module (`/api/users/`)
Handles registration, login, profile management, password changes, and admin user management.

### 2. Events Module (`/api/events/`)
Handles event creation, publishing, cancellation, search, filtering by category/location/date, and waitlist management.

### 3. Bookings Module (`/api/bookings/`)
Handles ticket booking with automatic capacity validation, booking confirmation, and cancellation with waitlist notification.

### 4. Tickets Module (`/api/tickets/`)
Handles QR code generation after booking confirmation, ticket download, and staff check-in verification.

### 5. Payments Module (`/api/payments/`)
Handles M-Pesa STK Push initiation, callback processing, and automatic booking confirmation after successful payment.

### 6. Reviews Module (`/api/reviews/`)
Handles post-event reviews and star ratings. Only attendees who attended an event can leave a review.

### 7. Notifications Module (`/api/notifications/`)
Handles in-app notifications for booking confirmations, event reminders, cancellations, and waitlist alerts.

### 8. Analytics Module (`/api/analytics/`)
Provides organizer dashboards with revenue, ticket sales, and attendance data, and admin-level platform statistics.

---

## Authentication

This project uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

### How it works

```
1. User sends POST /api/users/login/ with email and password
2. Server returns access token (expires in 60 min) and refresh token (expires in 7 days)
3. Client includes access token in every protected request:
   Authorization: Bearer <access_token>
4. When access token expires, client sends refresh token to get a new one
```

### Token Endpoints
```
POST /api/users/login/          → Get access + refresh tokens
POST /api/users/token/refresh/  → Get new access token using refresh token
POST /api/users/logout/         → Blacklist refresh token
```

---

## M-Pesa Integration

This project uses **Safaricom Daraja API** for M-Pesa STK Push payments.

### Payment Flow
```
1. Attendee selects event and quantity → booking created (status: pending)
2. Attendee sends phone number to /api/payments/initiate/
3. Server calls Daraja STK Push API → M-Pesa prompt appears on phone
4. Attendee enters M-Pesa PIN on their phone
5. Safaricom sends callback to /api/payments/mpesa/callback/
6. Server receives callback → updates payment status to completed
7. Booking status automatically updated to confirmed
8. QR ticket generated and ready for download
```

### Daraja Sandbox Credentials
```
Shortcode : 174379
Passkey   : bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
Test Phone: 254708374149
```

> For production, replace sandbox URLs in `payments/mpesa.py` with live Safaricom URLs.

---

## QR Ticket System

Each confirmed booking generates a unique QR ticket.

### QR Code Contents
```
EVENTHUB|<ticket_ref>|<event_title>|<user_email>
```

### Check-in Flow
```
1. Staff logs in with staff credentials
2. Staff scans QR code at event entrance
3. System verifies: valid ticket, not already used, event is active
4. If valid → checked_in = True, checked_in_at = current time
5. If already used → returns error "Ticket already used"
```

---

## Real-Time Features

Django Channels + Redis enables WebSocket communication for:

- **Live ticket counts** — when someone books, remaining tickets update instantly for all viewers
- **Real-time check-in stats** — attendance counter updates live during events

### WebSocket URL
```
ws://localhost:8000/ws/tickets/<event_id>/
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Redis (for real-time features)
- Git

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/eventhub.git
cd eventhub
```

### Step 2: Create and activate virtual environment
```bash
python -m venv my_env

# Windows
my_env\Scripts\activate

# Mac/Linux
source my_env/bin/activate
```

### Step 3: Install dependencies
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary Pillow qrcode[pil] channels==4.0.0 channels-redis==4.1.0 celery redis drf-yasg python-decouple requests
```

### Step 4: Create PostgreSQL database
```sql
CREATE DATABASE eventhub_db;
```

### Step 5: Configure environment variables
Create a `.env` file in the `backend/` folder (see Environment Variables section below).

### Step 6: Run migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create superuser
```bash
python manage.py createsuperuser
```

### Step 8: Start the server
```bash
python manage.py runserver
```

---

## Author

**Natasha Bolyn**

---
