from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.services import has_permission
from apps.notifications.services import create_notification
from apps.production.models import ProductionTask, TaskHistory, TaskParticipation
from apps.production.selectors import get_visible_task


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
    recipients = (
        User.objects.filter(pk=task.assigned_user_id)
        if task.assigned_user_id
        else User.objects.filter(
            memberships__organization_unit=task.assigned_unit,
            memberships__organization_unit__is_active=True,
        )
    )
    if recipients.exists():
        create_notification(
            recipients=recipients,
            event_type="task_assigned",
            title="Nowe zadanie produkcyjne",
            body=task.title,
            url=reverse("production:task-detail", args=[task.pk]),
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
    create_notification(
        recipients=User.objects.filter(pk=new_user.pk),
        event_type="task_transferred",
        title="Przekazano Ci zadanie",
        body=task.title,
        url=reverse("production:task-detail", args=[task.pk]),
    )
    return task


def _require_task_visibility(*, task, user):
    if get_visible_task(user=user, task_id=task.pk) is None:
        raise PermissionDenied("Nie masz dostępu do tego zadania.")


@transaction.atomic
def start_or_join_task(*, task, user):
    task = ProductionTask.objects.select_for_update().get(pk=task.pk)
    _require_task_visibility(task=task, user=user)
    if task.status in {ProductionTask.Status.COMPLETED, ProductionTask.Status.CANCELLED}:
        raise PermissionDenied("Nie można dołączyć do zamkniętego zadania.")

    participation = TaskParticipation.objects.filter(
        task=task, user=user, left_at__isnull=True
    ).first()
    if participation is not None:
        return participation

    participation = TaskParticipation.objects.create(task=task, user=user)
    previous_status = task.status
    if previous_status != ProductionTask.Status.IN_PROGRESS:
        task.status = ProductionTask.Status.IN_PROGRESS
        task.save(update_fields=["status", "updated_at"])
        TaskHistory.objects.create(
            task=task,
            event_type=TaskHistory.EventType.STATUS_CHANGED,
            actor=user,
            old_value=previous_status,
            new_value=task.status,
        )
    TaskHistory.objects.create(
        task=task,
        event_type=TaskHistory.EventType.PARTICIPANT_STARTED,
        actor=user,
        new_value=str(user),
        metadata={"participation_id": participation.pk},
    )
    return participation


@transaction.atomic
def leave_task(*, task, user, leave_note=""):
    task = ProductionTask.objects.select_for_update().get(pk=task.pk)
    _require_task_visibility(task=task, user=user)
    participation = TaskParticipation.objects.filter(
        task=task, user=user, left_at__isnull=True
    ).first()
    if participation is None:
        raise PermissionDenied("Nie jesteś aktywnym uczestnikiem tego zadania.")
    participation.left_at = timezone.now()
    participation.leave_note = leave_note.strip()
    participation.save(update_fields=["left_at", "leave_note"])
    TaskHistory.objects.create(
        task=task,
        event_type=TaskHistory.EventType.PARTICIPANT_LEFT,
        actor=user,
        old_value=str(user),
        new_value=participation.leave_note,
        metadata={"participation_id": participation.pk},
    )
    return participation


@transaction.atomic
def finish_task(*, task, actor):
    task = ProductionTask.objects.select_for_update().get(pk=task.pk)
    _require_task_visibility(task=task, user=actor)
    participations = list(
        TaskParticipation.objects.select_for_update()
        .filter(task=task, left_at__isnull=True)
        .select_related("user")
        .order_by("started_at", "pk")
    )
    if not any(participation.user_id == actor.pk for participation in participations):
        raise PermissionDenied("Tylko aktywny uczestnik może zakończyć zadanie.")

    finished_at = timezone.now()
    active_participants = [
        {
            "participation_id": participation.pk,
            "user_id": participation.user_id,
            "name": participation.user.get_full_name() or participation.user.username,
        }
        for participation in participations
    ]
    TaskParticipation.objects.filter(pk__in=[item.pk for item in participations]).update(
        left_at=finished_at
    )
    old_status = task.status
    task.status = ProductionTask.Status.COMPLETED
    task.save(update_fields=["status", "updated_at"])
    TaskHistory.objects.create(
        task=task,
        event_type=TaskHistory.EventType.COMPLETED,
        actor=actor,
        old_value=old_status,
        new_value=task.status,
        metadata={"active_participants": active_participants},
    )
    return task
