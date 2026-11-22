from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import Notification, NotificationRecipient


def _send_notification(user_id, payload):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "notification.message", "payload": payload},
    )


@transaction.atomic
def create_notification(*, recipients, event_type, title, body="", url=""):
    notification = Notification.objects.create(
        event_type=event_type, title=title, body=body, url=url
    )
    users = list(recipients.filter(is_active=True).distinct())
    NotificationRecipient.objects.bulk_create(
        [NotificationRecipient(notification=notification, user=user) for user in users]
    )
    payload = {
        "id": notification.pk,
        "event_type": notification.event_type,
        "title": notification.title,
        "body": notification.body,
        "url": notification.url,
        "created_at": timezone.localtime(notification.created_at).isoformat(),
    }
    for user in users:
        transaction.on_commit(
            lambda user_id=user.pk, message=payload: _send_notification(user_id, message)
        )
    return notification


def unread_notifications(*, user):
    return NotificationRecipient.objects.filter(user=user, is_read=False).select_related(
        "notification"
    )
