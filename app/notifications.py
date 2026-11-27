"""
Bookish Notification Service
Sends instant notifications to the store owner/admin when an order is placed or paid.
Supports:
1. Email (SMTP / Mail server if configured)
2. Telegram Bot (instant mobile push notification)
3. Custom Webhook (Discord / Slack / Zapier / Africa's Talking)
4. Application logging fallback
"""
import os
import smtplib
import logging
import urllib.request
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("bookish.notifications")

def get_admin_email():
    return os.getenv("ADMIN_NOTIFICATION_EMAIL") or os.getenv("ADMIN_EMAIL") or "admin@bookish.co"

def format_order_summary(order):
    items_text = []
    for item in order.items:
        title = item.book.title if item.book else "Unknown Book"
        fmt = f" ({item.variant.format})" if item.variant else ""
        items_text.append(f"  • {title}{fmt} × {item.quantity} — KES {item.unit_price_kes * item.quantity:,}")
    
    items_block = "\n".join(items_text) if items_text else "  (No items)"
    
    msg = f"""
📦 NEW BOOKISH ORDER: {order.reference}
===================================================
Status: {order.status.upper()}
Total: KES {order.total_kes:,}
Customer: {order.delivery_name or 'Anonymous'}
Phone: {order.delivery_phone or 'N/A'}
Email: {order.delivery_email or 'N/A'}
Delivery Address: {order.delivery_address or 'N/A'}
Notes: {order.delivery_notes or 'None'}

ITEMS:
{items_block}

Admin Dashboard: {os.getenv('SITE_URL', 'https://bookish-chi.vercel.app')}/admin
===================================================
""".strip()
    return msg

def send_email_notification(order, subject, body_text):
    smtp_server = os.getenv("SMTP_SERVER") or os.getenv("MAIL_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT") or os.getenv("MAIL_PORT") or 587)
    smtp_user = os.getenv("SMTP_USER") or os.getenv("MAIL_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD") or os.getenv("MAIL_PASSWORD")
    admin_email = get_admin_email()

    if not smtp_server or not smtp_user:
        logger.info(f"[Email Notification Skipped - SMTP not configured]: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Bookish Orders <{smtp_user}>"
        msg["To"] = admin_email
        msg.attach(MIMEText(body_text, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [admin_email], msg.as_string())
        logger.info(f"Email notification sent to {admin_email} for order {order.reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False

def send_telegram_notification(order, body_text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": body_text,
            "parse_mode": "HTML"
        }
        # Format HTML message for Telegram
        html_msg = f"<b>📚 New Bookish Order: {order.reference}</b>\n"
        html_msg += f"<b>Status:</b> {order.status.upper()}\n"
        html_msg += f"<b>Amount:</b> KES {order.total_kes:,}\n"
        html_msg += f"<b>Customer:</b> {order.delivery_name}\n"
        html_msg += f"<b>Phone:</b> <code>{order.delivery_phone}</code>\n"
        html_msg += f"<b>Address:</b> {order.delivery_address}\n"
        if order.delivery_notes:
            html_msg += f"<b>Notes:</b> {order.delivery_notes}\n"
        html_msg += "\n<b>Items:</b>\n"
        for item in order.items:
            t = item.book.title if item.book else "Book"
            html_msg += f"• {t} × {item.quantity} (KES {item.unit_price_kes * item.quantity:,})\n"
        
        payload["text"] = html_msg
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=8)
        logger.info(f"Telegram notification sent for order {order.reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False

def send_webhook_notification(order):
    webhook_url = os.getenv("ORDER_WEBHOOK_URL")
    if not webhook_url:
        return False

    try:
        payload = {
            "event": f"order.{order.status}",
            "order": {
                "reference": order.reference,
                "status": order.status,
                "total_kes": order.total_kes,
                "customer": {
                    "name": order.delivery_name,
                    "phone": order.delivery_phone,
                    "email": order.delivery_email,
                    "address": order.delivery_address,
                    "notes": order.delivery_notes,
                },
                "items": [
                    {
                        "title": item.book.title if item.book else "",
                        "quantity": item.quantity,
                        "unit_price_kes": item.unit_price_kes,
                        "total_price_kes": item.unit_price_kes * item.quantity,
                    }
                    for item in order.items
                ]
            }
        }
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Bookish-Store/1.0"}
        )
        urllib.request.urlopen(req, timeout=8)
        logger.info(f"Webhook notification dispatched for order {order.reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to dispatch webhook notification: {e}")
        return False

def notify_order_placed(order):
    """Called when an order is created (status = pending)."""
    subject = f"📦 New Order Placed: {order.reference} (KES {order.total_kes:,})"
    body = format_order_summary(order)
    logger.info(f"NOTIFICATION [Order Placed]:\n{body}")
    send_email_notification(order, subject, body)
    send_telegram_notification(order, body)
    send_webhook_notification(order)

def notify_order_paid(order):
    """Called when an order payment is confirmed (status = paid)."""
    subject = f"💰 ORDER PAID: {order.reference} — KES {order.total_kes:,}"
    body = format_order_summary(order)
    logger.info(f"NOTIFICATION [Order Paid]:\n{body}")
    send_email_notification(order, subject, body)
    send_telegram_notification(order, body)
    send_webhook_notification(order)
