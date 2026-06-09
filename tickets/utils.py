import qrcode
import uuid
from io import BytesIO
from django.core.files import File
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def generate_qr_code(ticket):
    """Generate QR code image for a ticket and save it"""
    qr_data = f"EVENTHUB|{ticket.ticket_ref}|{ticket.booking.event.title}|{ticket.booking.user.email}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    ticket.qr_code.save(f"{ticket.ticket_ref}.png", File(buffer), save=False)
    return ticket


def notify_ticket_update(event_id, remaining_tickets):
    """Send real-time ticket count update via WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'tickets_{event_id}',
        {
            'type': 'ticket_update',
            'remaining_tickets': remaining_tickets,
        }
    )