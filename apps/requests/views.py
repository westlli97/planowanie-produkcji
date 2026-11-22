from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.requests.forms import (
    ERPReferenceForm,
    ProductionRequestForm,
    RequestDueDateForm,
    RequestItemForm,
    RequestItemFormSet,
    RequestPriorityForm,
    RequestStatusForm,
)
from apps.requests.models import ProductionRequest
from apps.requests.selectors import get_request_list
from apps.requests.services import (
    can_change_priority,
    can_change_status,
    can_edit_due_date,
    can_update_erp_reference,
    change_erp_reference,
    change_request_due_date,
    change_request_priority,
    change_request_status,
    create_request_with_items,
)


def request_create(request):
    if request.method == "POST":
        request_form = ProductionRequestForm(request.POST)
        production_request = request_form.save(commit=False) if request_form.is_valid() else None
        formset = RequestItemFormSet(
            request.POST,
            instance=production_request,
            prefix="items",
        )
        if request_form.is_valid() and formset.is_valid():
            create_request_with_items(
                production_request=production_request,
                item_formset=formset,
                author=request.user,
            )
            messages.success(request, "Zgłoszenie zostało utworzone.")
            return redirect("requests:create")
    else:
        request_form = ProductionRequestForm(initial={"request_type": "OTHER"})
        formset = RequestItemFormSet(prefix="items")

    return render(
        request,
        "pages/request_create.html",
        {"request_form": request_form, "formset": formset},
    )


def request_item_add(request):
    try:
        index = int(request.GET.get("index", ""))
    except ValueError:
        return HttpResponseBadRequest("Nieprawidłowy numer pozycji.")
    if index < 0:
        return HttpResponseBadRequest("Nieprawidłowy numer pozycji.")
    form = RequestItemForm(prefix=f"items-{index}")
    return render(
        request,
        "components/request_item_form.html",
        {"form": form, "next_index": index + 1},
    )


def request_list(request):
    tab = "closed" if request.GET.get("tab") == "closed" else "open"
    query = request.GET.get("q", "")
    context = {
        "requests": get_request_list(tab=tab, query=query),
        "tab": tab,
        "query": query,
    }
    template = (
        "components/request_list_results.html"
        if request.headers.get("HX-Request") == "true"
        else "pages/request_list.html"
    )
    return render(request, template, context)


def request_detail(request, request_id):
    production_request = get_object_or_404(
        ProductionRequest.objects.select_related("author").prefetch_related(
            "items", "history__actor", "priority_history__actor"
        ),
        pk=request_id,
    )
    return render(
        request,
        "pages/request_detail.html",
        _request_detail_context(request, production_request),
    )


def _request_detail_context(request, production_request, **overrides):
    context = {
        "production_request": production_request,
        "can_change_status": can_change_status(
            user=request.user, production_request=production_request
        ),
        "can_change_priority": can_change_priority(user=request.user),
        "can_edit_due_date": can_edit_due_date(user=request.user),
        "can_update_erp_reference": can_update_erp_reference(user=request.user),
        "status_form": RequestStatusForm(initial={"status": production_request.status}),
        "priority_form": RequestPriorityForm(
            initial={"priority": production_request.priority}
        ),
        "due_date_form": RequestDueDateForm(initial={"due_date": production_request.due_date}),
        "erp_reference_form": ERPReferenceForm(
            initial={"erp_reference_number": production_request.erp_reference_number}
        ),
    }
    context.update(overrides)
    return context


def _update_request(
    request,
    request_id,
    *,
    form_class,
    service,
    form_field,
    service_field,
    success_message,
):
    production_request = get_object_or_404(
        ProductionRequest,
        pk=request_id,
    )
    form = form_class(request.POST)
    if form.is_valid():
        service(
            production_request=production_request,
            actor=request.user,
            **{service_field: form.cleaned_data[form_field]},
        )
        messages.success(request, success_message)
        return redirect("requests:detail", request_id=request_id)
    context = _request_detail_context(
        request, production_request, **{f"{form_field}_form": form}
    )
    return render(request, "pages/request_detail.html", context, status=400)


@require_POST
def request_status_update(request, request_id):
    return _update_request(
        request,
        request_id,
        form_class=RequestStatusForm,
        service=change_request_status,
        form_field="status",
        service_field="new_status",
        success_message="Status zgłoszenia został zmieniony.",
    )


@require_POST
def request_priority_update(request, request_id):
    return _update_request(
        request,
        request_id,
        form_class=RequestPriorityForm,
        service=change_request_priority,
        form_field="priority",
        service_field="new_priority",
        success_message="Priorytet zgłoszenia został zmieniony.",
    )


@require_POST
def request_due_date_update(request, request_id):
    return _update_request(
        request,
        request_id,
        form_class=RequestDueDateForm,
        service=change_request_due_date,
        form_field="due_date",
        service_field="due_date",
        success_message="Termin realizacji został zaktualizowany.",
    )


@require_POST
def request_erp_reference_update(request, request_id):
    return _update_request(
        request,
        request_id,
        form_class=ERPReferenceForm,
        service=change_erp_reference,
        form_field="erp_reference_number",
        service_field="erp_reference_number",
        success_message="Numer ERP został zapisany.",
    )
