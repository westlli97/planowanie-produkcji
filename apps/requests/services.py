from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.services import has_permission
from apps.notifications.services import create_notification
from apps.requests.models import PriorityHistory, RequestHistory


@transaction.atomic
def create_request_with_items(*, production_request, item_formset, author):
    production_request.author = author
    production_request.save()
    item_formset.instance = production_request
    item_formset.save()
    RequestHistory.objects.create(
        production_request=production_request,
        field_name="status",
        old_value="",
        new_value=production_request.status,
        actor=author,
    )
    PriorityHistory.objects.create(
        production_request=production_request,
        old_priority="",
        new_priority=production_request.priority,
        actor=author,
    )
    if author.worker_type == User.WorkerType.PRODUCTION:
        office_recipients = User.objects.filter(
            worker_type=User.WorkerType.OFFICE, is_active=True
        )
        if office_recipients.exists():
            create_notification(
                recipients=office_recipients,
                event_type="request_created",
                title="Nowe zgłoszenie z Produkcji",
                body=f"Zgłoszenie #{production_request.pk} zostało utworzone.",
                url=reverse("requests:detail", args=[production_request.pk]),
            )
    return production_request


def can_change_status(*, user, production_request):
    return (
        user.is_staff
        or user.is_superuser
        or user.worker_type == User.WorkerType.OFFICE
        or production_request.author_id == user.pk
        or has_permission(user, "requests.change_status")
    )


def can_change_priority(*, user):
    return has_permission(user, "requests.change_priority")


def can_edit_due_date(*, user):
    return has_permission(user, "requests.edit_due_date")


def can_update_erp_reference(*, user):
    return (
        user.is_staff
        or user.is_superuser
        or user.worker_type == User.WorkerType.OFFICE
        or has_permission(user, "requests.update_erp_reference")
    )


@transaction.atomic
def change_request_status(*, production_request, actor, new_status):
    if not can_change_status(user=actor, production_request=production_request):
        raise PermissionDenied("Nie masz uprawnień do zmiany statusu zgłoszenia.")
    old_status = production_request.status
    if old_status == new_status:
        return production_request
    production_request.status = new_status
    production_request.save(update_fields=["status", "updated_at"])
    RequestHistory.objects.create(
        production_request=production_request,
        field_name="status",
        old_value=old_status,
        new_value=new_status,
        actor=actor,
    )
    return production_request


@transaction.atomic
def change_request_priority(*, production_request, actor, new_priority):
    if not can_change_priority(user=actor):
        raise PermissionDenied("Nie masz uprawnień do zmiany priorytetu.")
    old_priority = production_request.priority
    if old_priority == new_priority:
        return production_request
    production_request.priority = new_priority
    production_request.save(update_fields=["priority", "updated_at"])
    PriorityHistory.objects.create(
        production_request=production_request,
        old_priority=old_priority,
        new_priority=new_priority,
        actor=actor,
    )
    return production_request


@transaction.atomic
def change_request_due_date(*, production_request, actor, due_date):
    if not can_edit_due_date(user=actor):
        raise PermissionDenied("Nie masz uprawnień do edycji terminu.")
    old_due_date = production_request.due_date
    if old_due_date == due_date:
        return production_request
    production_request.due_date = due_date
    production_request.save(update_fields=["due_date", "updated_at"])
    RequestHistory.objects.create(
        production_request=production_request,
        field_name="due_date",
        old_value=old_due_date.isoformat() if old_due_date else "",
        new_value=due_date.isoformat() if due_date else "",
        actor=actor,
    )
    return production_request


@transaction.atomic
def change_erp_reference(*, production_request, actor, erp_reference_number):
    if not can_update_erp_reference(user=actor):
        raise PermissionDenied("Nie masz uprawnień do wpisania numeru ERP.")
    old_reference = production_request.erp_reference_number
    if old_reference == erp_reference_number:
        return production_request
    production_request.erp_reference_number = erp_reference_number.strip()
    production_request.save(update_fields=["erp_reference_number", "updated_at"])
    RequestHistory.objects.create(
        production_request=production_request,
        field_name="erp_reference_number",
        old_value=old_reference,
        new_value=production_request.erp_reference_number,
        actor=actor,
    )
    return production_request
