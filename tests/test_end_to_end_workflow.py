import pytest
from django.urls import reverse

from apps.accounts.models import OrganizationUnit, User, UserMembership
from apps.notifications.models import NotificationRecipient
from apps.production.models import ProductionTask
from apps.requests.models import ProductionRequest


def create_request_payload():
    return {
        "request_type": ProductionRequest.RequestType.INDEX_ORDER,
        "priority": ProductionRequest.Priority.URGENT,
        "due_date": "",
        "erp_reference_number": "",
        "items-TOTAL_FORMS": "1",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",
        "items-0-erp_index": "ERP-E2E-500",
        "items-0-quantity": "",
        "items-0-unit": "",
        "items-0-comment": "Potrzebne do bieżącej produkcji",
    }


@pytest.mark.django_db
def test_end_to_end_request_to_completed_production_task(client):
    office = User.objects.create_user(
        username="e2e-office",
        password="Office-password-2026",
        worker_type=User.WorkerType.OFFICE,
        is_staff=True,
    )
    worker = User.objects.create_user(
        username="e2e-operator",
        first_name="Ewa",
        last_name="Lis",
        password="Worker-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )
    unit = OrganizationUnit.objects.create(name="Pakowalnia E2E")
    UserMembership.objects.create(user=worker, organization_unit=unit, is_primary=True)

    client.force_login(worker)
    request_response = client.post(reverse("requests:create"), create_request_payload())
    assert request_response.status_code == 302
    production_request = ProductionRequest.objects.get(author=worker)
    assert NotificationRecipient.objects.filter(user=office).exists()

    client.force_login(office)
    status_response = client.post(
        reverse("requests:status-update", args=[production_request.pk]),
        {"status": ProductionRequest.Status.IN_PROGRESS},
    )
    erp_response = client.post(
        reverse("requests:erp-reference-update", args=[production_request.pk]),
        {"erp_reference_number": "ERP-PO-9001"},
    )
    assert status_response.status_code == 302
    assert erp_response.status_code == 302

    task_response = client.post(
        reverse("production:task-create"),
        {
            "title": "Przygotuj materiał ERP-E2E-500",
            "description": "Przygotować pozycję ze zgłoszenia.",
            "assigned_unit": str(unit.pk),
            "assigned_user": "",
            "priority": ProductionTask.Priority.URGENT,
            "due_date": "",
            "production_request": str(production_request.pk),
        },
    )
    assert task_response.status_code == 302
    task = ProductionTask.objects.get(production_request=production_request)
    assert NotificationRecipient.objects.filter(
        notification__event_type="task_assigned", user=worker
    ).exists()

    client.force_login(worker)
    dashboard = client.get(reverse("dashboard:home"))
    assert dashboard.status_code == 200
    assert b"Przygotuj materia\xc5\x82 ERP-E2E-500" in dashboard.content
    assert b"Podsumowanie zg\xc5\x82osze\xc5\x84" not in dashboard.content

    join_response = client.post(reverse("production:task-join", args=[task.pk]))
    finish_response = client.post(reverse("production:task-finish", args=[task.pk]))
    assert join_response.status_code == 302
    assert finish_response.status_code == 302
    task.refresh_from_db()
    assert task.status == ProductionTask.Status.COMPLETED

    client.force_login(office)
    office_dashboard = client.get(reverse("dashboard:home"))
    assert office_dashboard.status_code == 200
    assert office_dashboard.context["request_summary"] == {"open_count": 1, "urgent_count": 1}
    assert b"Otwarte zg\xc5\x82oszenia" in office_dashboard.content
    assert b">1</span>" in office_dashboard.content
    assert b"Pilne zg\xc5\x82oszenia" in office_dashboard.content
