from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.production.forms import LeaveTaskForm, ProductionTaskForm, TaskTransferForm
from apps.production.models import ProductionTask, TaskParticipation
from apps.production.selectors import get_visible_task, get_visible_tasks
from apps.production.services import (
    can_transfer_task,
    create_production_task,
    finish_task,
    leave_task,
    start_or_join_task,
    transfer_individual_task,
)


def task_list(request):
    return render(
        request,
        "pages/task_list.html",
        {
            "tasks": get_visible_tasks(user=request.user),
            "can_transfer": can_transfer_task(user=request.user),
        },
    )


def task_create(request):
    form = ProductionTaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        create_production_task(task=task, actor=request.user)
        messages.success(request, "Zadanie zostało utworzone.")
        return redirect("production:task-list")
    return render(request, "pages/task_form.html", {"form": form})


def task_transfer(request, task_id):
    task = get_object_or_404(ProductionTask, pk=task_id)
    if not can_transfer_task(user=request.user):
        raise PermissionDenied("Nie masz uprawnień do przekazania zadania.")
    if task.assigned_user_id is None or task.assigned_unit_id is not None:
        raise PermissionDenied("Można przekazać wyłącznie zadanie indywidualne.")

    form = TaskTransferForm(request.POST or None, initial={"assigned_user": task.assigned_user_id})
    if request.method == "POST" and form.is_valid():
        transfer_individual_task(
            task=task,
            actor=request.user,
            new_user=form.cleaned_data["assigned_user"],
        )
        messages.success(request, "Zadanie zostało przekazane.")
        return redirect("production:task-list")
    return render(request, "pages/task_transfer.html", {"task": task, "form": form})


def _get_visible_task_or_404(request, task_id):
    task = get_visible_task(user=request.user, task_id=task_id)
    if task is None:
        raise Http404
    return task


def _task_state_context(request, task):
    active_participations = task.participations.filter(left_at__isnull=True).select_related(
        "user"
    )
    all_participations = task.participations.select_related("user")
    return {
        "task": task,
        "active_participations": active_participations,
        "participations": all_participations,
        "task_history": task.history.select_related("actor"),
        "is_active_participant": active_participations.filter(user=request.user).exists(),
        "has_participated": all_participations.exists(),
        "leave_form": LeaveTaskForm(),
    }


def task_detail(request, task_id):
    task = _get_visible_task_or_404(request, task_id)
    return render(
        request,
        "pages/task_detail.html",
        _task_state_context(request, task),
    )


def _render_task_state(request, task):
    task.refresh_from_db()
    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "components/task_state.html",
            _task_state_context(request, task),
        )
    return redirect("production:task-detail", task_id=task.pk)


@require_POST
def task_join(request, task_id):
    task = _get_visible_task_or_404(request, task_id)
    start_or_join_task(task=task, user=request.user)
    return _render_task_state(request, task)


@require_POST
def task_leave(request, task_id):
    task = _get_visible_task_or_404(request, task_id)
    form = LeaveTaskForm(request.POST)
    if not form.is_valid():
        context = _task_state_context(request, task)
        context["leave_form"] = form
        return render(request, "components/task_state.html", context, status=400)
    leave_task(
        task=task,
        user=request.user,
        leave_note=form.cleaned_data["leave_note"],
    )
    return _render_task_state(request, task)


def task_finish_confirmation(request, task_id):
    task = _get_visible_task_or_404(request, task_id)
    if not TaskParticipation.objects.filter(
        task=task, user=request.user, left_at__isnull=True
    ).exists():
        raise PermissionDenied("Tylko aktywny uczestnik może zakończyć zadanie.")
    active_participations = task.participations.filter(left_at__isnull=True).select_related(
        "user"
    )
    return render(
        request,
        "components/task_finish_confirmation.html",
        {"task": task, "active_participations": active_participations},
    )


@require_POST
def task_finish(request, task_id):
    task = _get_visible_task_or_404(request, task_id)
    finish_task(task=task, actor=request.user)
    response = _render_task_state(request, task)
    if request.headers.get("HX-Request") == "true":
        response.content += b'<div id="modal-container" hx-swap-oob="innerHTML"></div>'
    return response
