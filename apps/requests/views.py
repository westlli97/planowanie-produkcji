from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render

from apps.requests.forms import ProductionRequestForm, RequestItemForm, RequestItemFormSet
from apps.requests.selectors import get_request_list
from apps.requests.services import create_request_with_items


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
