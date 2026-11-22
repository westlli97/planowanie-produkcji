from django.db import transaction

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
    return production_request
