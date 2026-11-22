from apps.accounts.services import has_permission
from apps.production.models import ProductionTask
from apps.production.selectors import get_visible_tasks
from apps.requests.models import ProductionRequest
from apps.requests.selectors import OPEN_STATUSES


def get_dashboard_data(*, user):
    open_tasks = get_visible_tasks(user=user).exclude(
        status__in=[ProductionTask.Status.COMPLETED, ProductionTask.Status.CANCELLED]
    )
    can_view_request_summary = (
        user.is_staff
        or user.worker_type == "OFFICE"
        or has_permission(user, "requests.view_summary")
        or has_permission(user, "tasks.view_all")
    )
    summary = None
    if can_view_request_summary:
        open_requests = ProductionRequest.objects.filter(status__in=OPEN_STATUSES)
        summary = {
            "open_count": open_requests.count(),
            "urgent_count": open_requests.filter(
                priority=ProductionRequest.Priority.URGENT
            ).count(),
        }
    return {"active_tasks": open_tasks, "request_summary": summary}
