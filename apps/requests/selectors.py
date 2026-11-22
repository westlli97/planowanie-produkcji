from django.db.models import Q

from apps.requests.models import ProductionRequest

OPEN_STATUSES = [
    ProductionRequest.Status.NEW,
    ProductionRequest.Status.IN_PROGRESS,
    ProductionRequest.Status.WAITING,
]
CLOSED_STATUSES = [
    ProductionRequest.Status.COMPLETED,
    ProductionRequest.Status.CANCELLED,
]


def get_request_list(*, tab="open", query=""):
    statuses = CLOSED_STATUSES if tab == "closed" else OPEN_STATUSES
    requests = ProductionRequest.objects.filter(status__in=statuses)
    query = query.strip()
    if query:
        requests = requests.filter(
            Q(items__erp_index__icontains=query)
            | Q(erp_reference_number__icontains=query)
        ).distinct()
    return requests.select_related("author").prefetch_related("items")
