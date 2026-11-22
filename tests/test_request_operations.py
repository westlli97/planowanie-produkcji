from datetime import date

import pytest
from django.urls import reverse

from apps.accounts.models import AppPermission, User
from apps.accounts.services import set_permission_override
from apps.requests.models import (
    PriorityHistory,
    ProductionRequest,
    RequestHistory,
    RequestItem,
)


@pytest.fixture
def requester(db):
    return User.objects.create_user(
        username="request-owner",
        password="Owner-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )


@pytest.fixture
def production_request(requester):
    request = ProductionRequest.objects.create(
        author=requester,
        request_type=ProductionRequest.RequestType.OTHER,
        priority=ProductionRequest.Priority.NORMAL,
    )
    RequestItem.objects.create(production_request=request, comment="Opis pierwotny")
    return request


def test_regular_worker_gets_403_when_changing_priority_or_due_date(
    client, requester, production_request
):
    client.force_login(requester)

    priority_response = client.post(
        reverse("requests:priority-update", args=[production_request.pk]),
        {"priority": ProductionRequest.Priority.URGENT},
    )
    due_date_response = client.post(
        reverse("requests:due-date-update", args=[production_request.pk]),
        {"due_date": "2026-12-31"},
    )

    assert priority_response.status_code == 403
    assert due_date_response.status_code == 403
    assert not PriorityHistory.objects.filter(
        production_request=production_request, old_priority__gt=""
    ).exists()
    assert not RequestHistory.objects.filter(
        production_request=production_request, field_name="due_date"
    ).exists()


@pytest.mark.django_db
def test_author_can_change_status_and_change_is_recorded(
    client, requester, production_request
):
    client.force_login(requester)

    response = client.post(
        reverse("requests:status-update", args=[production_request.pk]),
        {"status": ProductionRequest.Status.IN_PROGRESS},
    )

    assert response.status_code == 302
    assert response.url == reverse("requests:detail", args=[production_request.pk])
    production_request.refresh_from_db()
    assert production_request.status == ProductionRequest.Status.IN_PROGRESS
    history = RequestHistory.objects.get(
        production_request=production_request, field_name="status", old_value="NEW"
    )
    assert production_request.status == ProductionRequest.Status.IN_PROGRESS
    assert history.new_value == ProductionRequest.Status.IN_PROGRESS
    assert history.actor == requester


@pytest.mark.django_db
def test_permission_grants_priority_and_due_date_updates_with_history(
    client, requester, production_request
):
    priority_permission = AppPermission.objects.create(
        code="requests.change_priority", name="Zmień priorytet"
    )
    due_permission = AppPermission.objects.create(
        code="requests.edit_due_date", name="Edytuj termin"
    )
    set_permission_override(permission=priority_permission, user=requester, allowed=True)
    set_permission_override(permission=due_permission, user=requester, allowed=True)
    client.force_login(requester)

    priority_response = client.post(
        reverse("requests:priority-update", args=[production_request.pk]),
        {"priority": ProductionRequest.Priority.URGENT},
    )
    due_date_response = client.post(
        reverse("requests:due-date-update", args=[production_request.pk]),
        {"due_date": "2026-12-31"},
    )

    assert priority_response.status_code == 302
    assert due_date_response.status_code == 302
    production_request.refresh_from_db()
    priority_change = PriorityHistory.objects.get(
        production_request=production_request, old_priority=ProductionRequest.Priority.NORMAL
    )
    due_change = RequestHistory.objects.get(
        production_request=production_request, field_name="due_date"
    )
    assert production_request.priority == ProductionRequest.Priority.URGENT
    assert priority_change.new_priority == ProductionRequest.Priority.URGENT
    assert priority_change.actor == requester
    assert production_request.due_date == date(2026, 12, 31)
    assert due_change.old_value == ""
    assert due_change.new_value == "2026-12-31"
    assert due_change.actor == requester


def test_office_can_enter_erp_reference_and_change_is_recorded(
    client, production_request, db
):
    office_user = User.objects.create_user(
        username="office-operator",
        password="Office-password-2026",
        worker_type=User.WorkerType.OFFICE,
    )
    client.force_login(office_user)

    response = client.post(
        reverse("requests:erp-reference-update", args=[production_request.pk]),
        {"erp_reference_number": "  ERP-REF-2026  "},
    )

    assert response.status_code == 302
    production_request.refresh_from_db()
    history = RequestHistory.objects.get(
        production_request=production_request, field_name="erp_reference_number"
    )
    assert production_request.erp_reference_number == "ERP-REF-2026"
    assert history.actor == office_user


@pytest.mark.django_db
def test_detail_page_shows_creation_comment_without_chat(client, requester, production_request):
    client.force_login(requester)

    response = client.get(reverse("requests:detail", args=[production_request.pk]))

    assert response.status_code == 200
    assert b"Opis pierwotny" in response.content
    assert b"Pozycje i komentarze" in response.content
