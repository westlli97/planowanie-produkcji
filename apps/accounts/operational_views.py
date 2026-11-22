from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.forms import (
    AppPermissionForm,
    FunctionAssignmentForm,
    JobFunctionForm,
    MembershipForm,
    OrganizationUnitForm,
    PermissionOverrideForm,
    WorkerTypePermissionForm,
)
from apps.accounts.models import (
    AppPermission,
    JobFunction,
    OrganizationUnit,
    WorkerTypePermission,
)
from apps.accounts.selectors import get_organization_units
from apps.accounts.services import (
    assign_job_function,
    assign_membership,
    save_organization_unit,
    set_organization_unit_active,
    set_permission_override,
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
        saved_unit = save_organization_unit(unit=unit, **form.cleaned_data)
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


def permission_panel_context(**overrides):
    context = {
        "permissions": AppPermission.objects.all(),
        "functions": JobFunction.objects.prefetch_related("permissions"),
        "permission_form": AppPermissionForm(),
        "assignment_form": FunctionAssignmentForm(),
        "override_form": PermissionOverrideForm(),
        "worker_type_form": WorkerTypePermissionForm(),
    }
    context.update(overrides)
    return context


@admin_required
def permission_panel(request):
    return render(
        request, "pages/permission_panel.html", permission_panel_context()
    )


@admin_required
def job_function_edit(request, function_id=None):
    job_function = (
        get_object_or_404(JobFunction, pk=function_id) if function_id is not None else None
    )
    form = JobFunctionForm(request.POST or None, instance=job_function)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Funkcja została zapisana.")
        return redirect("accounts:permission-panel")
    return render(request, "pages/job_function_form.html", {"form": form})


@admin_required
@require_POST
def permission_create(request):
    form = AppPermissionForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Uprawnienie zostało dodane.")
        return redirect("accounts:permission-panel")
    context = permission_panel_context(permission_form=form)
    return render(request, "pages/permission_panel.html", context)


@admin_required
@require_POST
def function_assignment_add(request):
    form = FunctionAssignmentForm(request.POST)
    if form.is_valid():
        assign_job_function(**form.cleaned_data)
        messages.success(request, "Funkcja została przypisana użytkownikowi.")
        return redirect("accounts:permission-panel")
    context = permission_panel_context(assignment_form=form)
    return render(request, "pages/permission_panel.html", context)


@admin_required
@require_POST
def permission_override_add(request):
    form = PermissionOverrideForm(request.POST)
    if form.is_valid():
        try:
            set_permission_override(**form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error.message)
        else:
            messages.success(request, "Nadpisanie uprawnienia zostało zapisane.")
            return redirect("accounts:permission-panel")
    context = permission_panel_context(override_form=form)
    return render(request, "pages/permission_panel.html", context)


@admin_required
@require_POST
def worker_type_permission_add(request):
    form = WorkerTypePermissionForm(request.POST)
    if form.is_valid():
        WorkerTypePermission.objects.get_or_create(**form.cleaned_data)
        messages.success(request, "Domyślne uprawnienie typu pracownika zostało zapisane.")
        return redirect("accounts:permission-panel")
    context = permission_panel_context(worker_type_form=form)
    return render(request, "pages/permission_panel.html", context)
