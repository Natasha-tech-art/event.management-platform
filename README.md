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

## Technology Stack

### Backend
| Technology | Version | Role |
|---|---|---|
| Django | 6.0.6 | Core backend framework |
| Django REST Framework | 3.15 | REST API development |
| PostgreSQL | 18 | Primary database |
| JWT (SimpleJWT) | Latest | Authentication & authorization |
| Django Channels | 4.0 | WebSocket real-time communication |
| Redis | Latest | Channel layer & message broker |
| Celery | Latest | Background task processing |
| qrcode | Latest | QR ticket generation |
| Pillow | Latest | Image processing |
| drf-yasg | Latest | Swagger API documentation |
| python-decouple | Latest | Environment variable management |

### Payment
| Technology | Role |
|---|---|
| Safaricom Daraja API | M-Pesa STK Push payment integration |

---

## Database Design

### Users Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| name | CharField | Full name |
| email | EmailField | Unique login email |
| password | CharField | Hashed password |
| role | CharField | attendee / organizer / staff / admin |
| profile_photo | ImageField | Profile picture |
| is_active | Boolean | Account status |
| date_joined | DateTime | Registration date |

### Events Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| organizer | ForeignKey | Links to User |
| title | CharField | Event name |
| description | TextField | Full description |
| category | ForeignKey | Links to Category |
| venue | CharField | Venue name |
| location | CharField | Physical location |
| start_date | DateTime | Event start |
| end_date | DateTime | Event end |
| ticket_price | Decimal | Price per ticket |
| capacity | Integer | Maximum attendees |
| banner | ImageField | Event banner image |
| status | CharField | draft / published / cancelled / completed |

### Bookings Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| user | ForeignKey | Links to User |
| event | ForeignKey | Links to Event |
| ticket_quantity | Integer | Number of tickets |
| total_amount | Decimal | Calculated total |
| booking_date | DateTime | When booked |
| status | CharField | pending / confirmed / cancelled |
| payment_ref | CharField | M-Pesa reference |

### Tickets Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| booking | OneToOne | Links to Booking |
| ticket_ref | CharField | Unique e.g. EVT-1-ABC12345 |
| qr_code | ImageField | Generated QR image |
| checked_in | Boolean | Entry status |
| checked_in_at | DateTime | Check-in timestamp |

### Payments Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| booking | OneToOne | Links to Booking |
| amount | Decimal | Payment amount |
| phone_number | CharField | M-Pesa phone number |
| mpesa_code | CharField | M-Pesa receipt code |
| checkout_request_id | CharField | Daraja request ID |
| status | CharField | pending / completed / failed |

### Reviews Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| event | ForeignKey | Links to Event |
| user | ForeignKey | Links to User |
| rating | Integer | 1 to 5 stars |
| comment | TextField | Review text |
| created_at | DateTime | Review date |

### Notifications Table
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| user | ForeignKey | Links to User |
| message | TextField | Notification content |
| read | Boolean | Read status |
| created_at | DateTime | Created timestamp |

---

## User Roles & Permissions

| Role | Permissions |
|---|---|
| **Attendee** | Register, browse events, book tickets, view bookings, download tickets, leave reviews, manage notifications |
| **Organizer** | All attendee permissions + create/edit/publish/cancel events, view event analytics, manage attendees |
| **Staff** | Scan QR tickets, verify attendees, view attendance statistics |
| **Admin** | Full system access — manage users, approve events, view platform analytics, generate reports |

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
Final Year Capstone Project
Event Management Platform — Backend API

---
