from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.production.forms import ProductionTaskForm, TaskTransferForm
from apps.production.models import ProductionTask
from apps.production.selectors import get_visible_tasks
from apps.production.services import (
    can_transfer_task,
    create_production_task,
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
