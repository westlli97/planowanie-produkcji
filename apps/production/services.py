from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts.services import has_permission
from apps.production.models import TaskHistory


@transaction.atomic
def create_production_task(*, task, actor):
    task.created_by = actor
    task.full_clean()
    task.save()
    assignee = task.assigned_unit or task.assigned_user
    TaskHistory.objects.create(
        task=task,
        event_type=TaskHistory.EventType.CREATED,
        actor=actor,
        new_value=str(assignee),
        metadata={"priority": task.priority, "status": task.status},
    )
    return task


def can_transfer_task(*, user):
    return has_permission(user, "tasks.transfer")


@transaction.atomic
def transfer_individual_task(*, task, actor, new_user):
    if not can_transfer_task(user=actor):
        raise PermissionDenied("Nie masz uprawnień do przekazania zadania.")
    if task.assigned_user_id is None or task.assigned_unit_id is not None:
        raise PermissionDenied("Można przekazać wyłącznie zadanie indywidualne.")
    old_user = task.assigned_user
    if old_user.pk == new_user.pk:
        return task
    task.assigned_user = new_user
    task.save(update_fields=["assigned_user", "updated_at"])
    TaskHistory.objects.create(
        task=task,
        event_type=TaskHistory.EventType.TRANSFERRED,
        actor=actor,
        old_value=str(old_user),
        new_value=str(new_user),
    )
    return task
