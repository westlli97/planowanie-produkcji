from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.forms import MembershipForm, OrganizationUnitForm
from apps.accounts.models import OrganizationUnit
from apps.accounts.selectors import get_organization_units
from apps.accounts.services import (
    assign_membership,
    save_organization_unit,
    set_organization_unit_active,
)

admin_required = user_passes_test(lambda user: user.is_staff)


@admin_required
def organization_panel(request):
    return render(
        request,
        "pages/organization_panel.html",
        {
            "units": get_organization_units(),
            "unit_form": OrganizationUnitForm(),
            "membership_form": MembershipForm(),
        },
    )


@admin_required
def organization_unit_edit(request, unit_id=None):
    unit = get_object_or_404(OrganizationUnit, pk=unit_id) if unit_id else None
    form = OrganizationUnitForm(request.POST or None, instance=unit)
    if request.method == "POST" and form.is_valid():
        saved_unit = save_organization_unit(
            unit=unit, **form.cleaned_data
        )
        messages.success(request, f"Jednostka „{saved_unit.name}” została zapisana.")
        return redirect("accounts:organization-panel")
    return render(request, "pages/organization_unit_form.html", {"form": form, "unit": unit})


@admin_required
@require_POST
def organization_membership_add(request):
    form = MembershipForm(request.POST)
    if form.is_valid():
        try:
            assign_membership(**form.cleaned_data)
        except ValidationError as error:
            form.add_error("organization_unit", error.message)
        else:
            messages.success(request, "Przynależność użytkownika została zapisana.")
            return redirect("accounts:organization-panel")
    return render(
        request,
        "pages/organization_unit_form.html",
        {"form": form, "form_title": "Przypisz użytkownika"},
    )


@admin_required
@require_POST
def organization_unit_toggle(request, unit_id):
    unit = get_object_or_404(OrganizationUnit, pk=unit_id)
    set_organization_unit_active(unit=unit, is_active=not unit.is_active)
    messages.success(request, f"Zmieniono aktywność jednostki „{unit.name}”.")
    return redirect("accounts:organization-panel")
