import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import OrganizationUnit, User
from apps.production.models import ProductionTask, TaskHistory, TaskParticipation


@pytest.fixture
def worker(db):
    return User.objects.create_user(
        username="task-worker",
        password="Task-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )


@pytest.fixture
def task(worker):
    unit = OrganizationUnit.objects.create(name="Pakowalnia")
    return ProductionTask.objects.create(
        title="Spakuj zamówienie",
        assigned_unit=unit,
        created_by=worker,
    )


@pytest.mark.django_db
def test_worker_can_have_multiple_historical_participation_periods(worker, task):
    first_start = timezone.now() - timezone.timedelta(hours=2)
    first_leave = first_start + timezone.timedelta(minutes=35)
    TaskParticipation.objects.create(
        task=task,
        user=worker,
        started_at=first_start,
        left_at=first_leave,
        leave_note="Brak materiału",
    )
    second_start = timezone.now()
    second = TaskParticipation.objects.create(task=task, user=worker, started_at=second_start)
    TaskHistory.objects.create(
        task=task,
        event_type=TaskHistory.EventType.PARTICIPANT_STARTED,
        actor=worker,
        metadata={"participation_id": second.pk},
    )

    periods = list(TaskParticipation.objects.filter(task=task, user=worker))
    assert len(periods) == 2
    assert periods[0].left_at == first_leave
    assert periods[0].leave_note == "Brak materiału"
    assert periods[1].left_at is None
    assert TaskHistory.objects.filter(task=task).count() == 1


@pytest.mark.django_db
def test_task_requires_exactly_one_assignee(worker):
    task = ProductionTask(title="Nieprzypisane", created_by=worker)

    with pytest.raises(ValidationError, match="jednej jednostki"):
        task.full_clean()


@pytest.mark.django_db
def test_task_cannot_have_both_unit_and_individual_assignee(worker):
    unit = OrganizationUnit.objects.create(name="Szlifiernia")
    task = ProductionTask(
        title="Podwójne przypisanie",
        assigned_unit=unit,
        assigned_user=worker,
        created_by=worker,
    )

    with pytest.raises(ValidationError, match="jednej jednostki"):
        task.full_clean()
