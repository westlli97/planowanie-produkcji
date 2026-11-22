import pytest
from django.urls import reverse

from apps.accounts.models import (
    AppPermission,
    OrganizationUnit,
    User,
    UserMembership,
)
from apps.accounts.services import set_permission_override
from apps.production.models import ProductionTask, TaskHistory


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="task-coordinator",
        password="Coordinator-password-2026",
        worker_type=User.WorkerType.OFFICE,
        is_staff=True,
    )


@pytest.fixture
def production_worker(db):
    return User.objects.create_user(
        username="floor-worker",
        password="Worker-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )


@pytest.mark.django_db
def test_task_visibility_is_limited_to_membership_units_and_individual_assignment(
    client, staff_user, production_worker
):
    unit_a = OrganizationUnit.objects.create(name="Pakowalnia")
    unit_b = OrganizationUnit.objects.create(name="Szlifiernia")
    UserMembership.objects.create(user=production_worker, organization_unit=unit_a, is_primary=True)
    visible_unit_task = ProductionTask.objects.create(
        title="Zadanie pakowalni",
        assigned_unit=unit_a,
        created_by=staff_user,
    )
    hidden_unit_task = ProductionTask.objects.create(
        title="Zadanie szlifierni",
        assigned_unit=unit_b,
        created_by=staff_user,
    )
    personal_task = ProductionTask.objects.create(
        title="Zadanie indywidualne",
        assigned_user=production_worker,
        created_by=staff_user,
    )
    ProductionTask.objects.create(
        title="Inne zadanie osobiste",
        assigned_user=staff_user,
        created_by=staff_user,
    )
    client.force_login(production_worker)

    response = client.get(reverse("production:task-list"))

    assert response.status_code == 200
    assert visible_unit_task.title.encode() in response.content
    assert personal_task.title.encode() in response.content
    assert hidden_unit_task.title.encode() not in response.content
    assert b"Inne zadanie osobiste" not in response.content


@pytest.mark.django_db
def test_view_all_permission_includes_tasks_from_other_units(
    client, staff_user, production_worker
):
    unit = OrganizationUnit.objects.create(name="Laser")
    task = ProductionTask.objects.create(
        title="Zadanie innego działu", assigned_unit=unit, created_by=staff_user
    )
    permission = AppPermission.objects.create(code="tasks.view_all", name="Wszystkie zadania")
    set_permission_override(permission=permission, user=production_worker, allowed=True)
    client.force_login(production_worker)

    response = client.get(reverse("production:task-list"))

    assert response.status_code == 200
    assert task.title.encode() in response.content


@pytest.mark.django_db
def test_supervisor_sees_individual_tasks_for_members_of_their_units(
    client, staff_user, production_worker
):
    supervisor = User.objects.create_user(
        username="floor-supervisor",
        password="Supervisor-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )
    unit = OrganizationUnit.objects.create(name="Montaż")
    UserMembership.objects.create(user=supervisor, organization_unit=unit, is_primary=True)
    UserMembership.objects.create(user=production_worker, organization_unit=unit, is_primary=True)
    team_task = ProductionTask.objects.create(
        title="Zadanie pracownika zespołu",
        assigned_user=production_worker,
        created_by=staff_user,
    )
    permission = AppPermission.objects.create(code="tasks.supervise", name="Nadzoruj zadania")
    set_permission_override(permission=permission, user=supervisor, allowed=True)
    client.force_login(supervisor)

    response = client.get(reverse("production:task-list"))

    assert response.status_code == 200
    assert team_task.title.encode() in response.content


@pytest.mark.django_db
def test_task_creation_records_author_priority_and_history(client, staff_user, production_worker):
    unit = OrganizationUnit.objects.create(name="Pakowalnia")
    client.force_login(staff_user)

    response = client.post(
        reverse("production:task-create"),
        {
            "title": "Pilne pakowanie",
            "description": "Przygotować serię do wysyłki.",
            "assigned_unit": str(unit.pk),
            "assigned_user": "",
            "priority": ProductionTask.Priority.URGENT,
            "due_date": "",
            "production_request": "",
        },
    )

    assert response.status_code == 302
    task = ProductionTask.objects.get(title="Pilne pakowanie")
    history = TaskHistory.objects.get(task=task)
    assert task.created_by == staff_user
    assert task.priority == ProductionTask.Priority.URGENT
    assert history.actor == staff_user
    assert history.metadata["priority"] == ProductionTask.Priority.URGENT


@pytest.mark.django_db
def test_only_authorized_user_can_transfer_an_individual_task(
    client, staff_user, production_worker
):
    successor = User.objects.create_user(
        username="next-worker",
        password="Next-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )
    task = ProductionTask.objects.create(
        title="Przekazywane zadanie", assigned_user=production_worker, created_by=staff_user
    )
    client.force_login(production_worker)

    denied = client.post(
        reverse("production:task-transfer", args=[task.pk]),
        {"assigned_user": str(successor.pk)},
    )
    assert denied.status_code == 403

    permission = AppPermission.objects.create(code="tasks.transfer", name="Przekaż zadanie")
    set_permission_override(permission=permission, user=production_worker, allowed=True)
    allowed = client.post(
        reverse("production:task-transfer", args=[task.pk]),
        {"assigned_user": str(successor.pk)},
    )

    assert allowed.status_code == 302
    task.refresh_from_db()
    event = TaskHistory.objects.get(task=task, event_type=TaskHistory.EventType.TRANSFERRED)
    assert task.assigned_user == successor
    assert event.actor == production_worker
    assert event.old_value == str(production_worker)
    assert event.new_value == str(successor)


@pytest.mark.django_db
def test_team_task_cannot_be_transferred(client, staff_user, production_worker):
    unit = OrganizationUnit.objects.create(name="Produkcja")
    task = ProductionTask.objects.create(
        title="Zadanie zespołowe", assigned_unit=unit, created_by=staff_user
    )
    permission = AppPermission.objects.create(code="tasks.transfer", name="Przekaż zadanie")
    set_permission_override(permission=permission, user=production_worker, allowed=True)
    client.force_login(production_worker)

    response = client.post(
        reverse("production:task-transfer", args=[task.pk]),
        {"assigned_user": str(staff_user.pk)},
    )

    assert response.status_code == 403
    task.refresh_from_db()
    assert task.assigned_user is None
    assert not TaskHistory.objects.filter(
        task=task, event_type=TaskHistory.EventType.TRANSFERRED
    ).exists()
