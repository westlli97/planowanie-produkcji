import pytest
from django.urls import reverse

from apps.accounts.models import OrganizationUnit, User, UserMembership
from apps.production.models import ProductionTask, TaskHistory, TaskParticipation


@pytest.fixture
def task_team(db):
    unit = OrganizationUnit.objects.create(name="Pakowalnia")
    first = User.objects.create_user(
        username="anna-worker",
        first_name="Anna",
        last_name="Kowalska",
        password="Anna-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )
    second = User.objects.create_user(
        username="jan-worker",
        first_name="Jan",
        last_name="Nowak",
        password="Jan-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )
    UserMembership.objects.create(user=first, organization_unit=unit, is_primary=True)
    UserMembership.objects.create(user=second, organization_unit=unit, is_primary=True)
    task = ProductionTask.objects.create(
        title="Spakuj partię 52",
        assigned_unit=unit,
        created_by=first,
    )
    return task, first, second


def test_two_workers_leave_rejoin_and_finish_task(client, task_team):
    task, first, second = task_team
    join_url = reverse("production:task-join", args=[task.pk])
    leave_url = reverse("production:task-leave", args=[task.pk])
    finish_url = reverse("production:task-finish", args=[task.pk])

    client.force_login(first)
    assert client.post(join_url).status_code == 302
    client.force_login(second)
    assert client.post(join_url).status_code == 302

    client.force_login(first)
    left_response = client.post(leave_url, {"leave_note": "Brak kartonów"})
    assert left_response.status_code == 302
    first_period = TaskParticipation.objects.get(task=task, user=first)
    task.refresh_from_db()
    assert first_period.left_at is not None
    assert first_period.leave_note == "Brak kartonów"
    assert task.status == ProductionTask.Status.IN_PROGRESS
    assert TaskParticipation.objects.filter(task=task, user=second, left_at__isnull=True).exists()

    assert client.post(join_url).status_code == 302
    assert TaskParticipation.objects.filter(task=task, user=first).count() == 2
    active_periods = TaskParticipation.objects.filter(
        task=task, user=first, left_at__isnull=True
    )
    assert active_periods.count() == 1

    client.force_login(second)
    confirmation = client.get(
        reverse("production:task-finish-confirmation", args=[task.pk])
    )
    assert confirmation.status_code == 200
    assert b"Anna Kowalska" in confirmation.content
    assert b"Jan Nowak" in confirmation.content

    response = client.post(finish_url)

    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == ProductionTask.Status.COMPLETED
    assert not TaskParticipation.objects.filter(task=task, left_at__isnull=True).exists()
    assert TaskParticipation.objects.filter(task=task, user=first).count() == 2
    completion = TaskHistory.objects.get(task=task, event_type=TaskHistory.EventType.COMPLETED)
    assert completion.actor == second
    assert completion.new_value == ProductionTask.Status.COMPLETED
    assert {item["name"] for item in completion.metadata["active_participants"]} == {
        "Anna Kowalska",
        "Jan Nowak",
    }
    assert TaskHistory.objects.filter(
        task=task, event_type=TaskHistory.EventType.PARTICIPANT_LEFT
    ).count() == 1


@pytest.mark.django_db
def test_last_participant_leaving_keeps_task_open_for_rejoining(client, task_team):
    task, first, _ = task_team
    client.force_login(first)
    client.post(reverse("production:task-join", args=[task.pk]))

    response = client.post(
        reverse("production:task-leave", args=[task.pk]), {"leave_note": "Przerwa"}
    )

    task.refresh_from_db()
    assert response.status_code == 302
    assert task.status == ProductionTask.Status.IN_PROGRESS
    assert not TaskParticipation.objects.filter(task=task, left_at__isnull=True).exists()
    assert client.post(reverse("production:task-join", args=[task.pk])).status_code == 302
    assert TaskParticipation.objects.filter(task=task, user=first).count() == 2


@pytest.mark.django_db
def test_nonparticipant_cannot_finish_task(client, task_team):
    task, first, second = task_team
    client.force_login(first)
    client.post(reverse("production:task-join", args=[task.pk]))
    client.force_login(second)

    response = client.post(reverse("production:task-finish", args=[task.pk]))

    assert response.status_code == 403
    task.refresh_from_db()
    assert task.status == ProductionTask.Status.IN_PROGRESS
    assert TaskParticipation.objects.filter(task=task, left_at__isnull=True).count() == 1


def test_task_detail_shows_all_participation_periods(client, task_team):
    task, first, _ = task_team
    TaskParticipation.objects.create(task=task, user=first, leave_note="Wyjście")
    client.force_login(first)

    response = client.get(reverse("production:task-detail", args=[task.pk]))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Historia uczestnictwa" in content
    assert "Wyjście" in content
    assert "Zakończ zadanie" in content
