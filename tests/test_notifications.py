import pytest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.test import Client
from django.urls import reverse

from apps.accounts.models import OrganizationUnit, User, UserMembership
from apps.notifications.models import Notification, NotificationRecipient
from apps.notifications.services import create_notification
from config.asgi import application


@pytest.fixture
def office_users(db):
    return [
        User.objects.create_user(
            username=f"office-{index}",
            password="Office-password-2026",
            worker_type=User.WorkerType.OFFICE,
        )
        for index in range(2)
    ]


@pytest.fixture
def production_users(db):
    return [
        User.objects.create_user(
            username=f"production-{index}",
            password="Production-password-2026",
            worker_type=User.WorkerType.PRODUCTION,
        )
        for index in range(2)
    ]


@pytest.mark.django_db
def test_notification_service_persists_recipients(office_users):
    notification = create_notification(
        recipients=User.objects.filter(pk__in=[user.pk for user in office_users]),
        event_type="request_created",
        title="Nowe zgłoszenie",
        body="Zgłoszenie #12",
        url="/requests/12/",
    )

    assert Notification.objects.get(pk=notification.pk).title == "Nowe zgłoszenie"
    assert set(
        NotificationRecipient.objects.filter(notification=notification).values_list(
            "user_id", flat=True
        )
    ) == {user.pk for user in office_users}
    unread_count = NotificationRecipient.objects.filter(
        notification=notification, is_read=False
    ).count()
    assert unread_count == 2


@pytest.mark.django_db
def test_production_request_notifies_only_office_users(client, office_users, production_users):
    requester = production_users[0]
    client.force_login(requester)
    response = client.post(
        reverse("requests:create"),
        {
            "request_type": "OTHER",
            "priority": "NORMAL",
            "due_date": "",
            "erp_reference_number": "",
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-erp_index": "",
            "items-0-quantity": "",
            "items-0-unit": "",
            "items-0-comment": "Uszkodzona maszyna",
        },
    )

    assert response.status_code == 302
    notification = Notification.objects.get(event_type="request_created")
    recipients = set(
        NotificationRecipient.objects.filter(notification=notification).values_list(
            "user_id", flat=True
        )
    )
    assert recipients == {user.pk for user in office_users}
    assert requester.pk not in recipients


@pytest.mark.django_db
def test_new_team_task_notifies_only_members_of_assigned_unit(
    client, office_users, production_users
):
    unit = OrganizationUnit.objects.create(name="Montaż")
    for user in production_users:
        UserMembership.objects.create(user=user, organization_unit=unit)
    client.force_login(office_users[0])

    response = client.post(
        reverse("production:task-create"),
        {
            "title": "Zmontuj serię 20",
            "description": "",
            "assigned_unit": str(unit.pk),
            "assigned_user": "",
            "priority": "NORMAL",
            "due_date": "",
            "production_request": "",
        },
    )

    assert response.status_code == 302
    notification = Notification.objects.get(event_type="task_assigned")
    recipients = set(
        NotificationRecipient.objects.filter(notification=notification).values_list(
            "user_id", flat=True
        )
    )
    assert recipients == {user.pk for user in production_users}


@pytest.mark.django_db(transaction=True)
def test_authenticated_websocket_receives_notification(office_users):
    user = office_users[0]
    client = Client()
    client.force_login(user)
    cookie = client.cookies[settings.SESSION_COOKIE_NAME].value
    communicator = WebsocketCommunicator(
        application,
        "/ws/notifications/",
        headers=[
            (b"cookie", f"{settings.SESSION_COOKIE_NAME}={cookie}".encode()),
            (b"origin", b"http://localhost"),
        ],
    )

    async def communicate():
        connected, _ = await communicator.connect()
        if not connected:
            return connected, None
        await get_channel_layer().group_send(
            f"user_{user.pk}",
            {
                "type": "notification.message",
                "payload": {"title": "Nowy wpis", "body": "Masz zgłoszenie"},
            },
        )
        message = await communicator.receive_json_from(timeout=2)
        await communicator.disconnect()
        return connected, message

    connected, message = async_to_sync(communicate)()

    assert connected
    assert message == {"title": "Nowy wpis", "body": "Masz zgłoszenie"}


@pytest.mark.django_db
def test_user_can_view_only_their_unread_notifications(client, office_users, production_users):
    notification = create_notification(
        recipients=User.objects.filter(pk=office_users[0].pk),
        event_type="test",
        title="Tylko moje",
    )
    client.force_login(office_users[0])

    response = client.get(reverse("notifications:unread-list"))

    assert response.status_code == 200
    assert b"Tylko moje" in response.content
    assert NotificationRecipient.objects.filter(
        notification=notification, user=production_users[0]
    ).count() == 0
