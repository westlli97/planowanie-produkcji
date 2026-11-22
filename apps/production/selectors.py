from django.db.models import Q

from apps.accounts.models import UserMembership
from apps.accounts.services import has_permission
from apps.production.models import ProductionTask


def get_visible_tasks(*, user):
    tasks = ProductionTask.objects.select_related(
        "assigned_unit", "assigned_user", "created_by", "production_request"
    ).prefetch_related("participations__user")
    if user.is_staff or user.is_superuser or has_permission(user, "tasks.view_all"):
        return tasks

    unit_ids = UserMembership.objects.filter(
        user=user, organization_unit__is_active=True
    ).values_list("organization_unit_id", flat=True)
    visibility_filter = Q(assigned_user=user) | Q(assigned_unit_id__in=unit_ids)
    if has_permission(user, "tasks.supervise"):
        team_user_ids = UserMembership.objects.filter(
            organization_unit_id__in=unit_ids,
            organization_unit__is_active=True,
        ).values_list("user_id", flat=True)
        visibility_filter |= Q(assigned_user_id__in=team_user_ids)
    return tasks.filter(visibility_filter).distinct()



def get_visible_task(*, user, task_id):
    return get_visible_tasks(user=user).filter(pk=task_id).first()
