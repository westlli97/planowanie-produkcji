from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import OrganizationUnit
from apps.requests.models import ProductionRequest


class ProductionTask(models.Model):
    class Priority(models.TextChoices):
        NORMAL = "NORMAL", "Normalny"
        URGENT = "URGENT", "Pilny"

    class Status(models.TextChoices):
        NEW = "NEW", "Nowe"
        ACCEPTED = "ACCEPTED", "Przyjęte do realizacji"
        IN_PROGRESS = "IN_PROGRESS", "W trakcie"
        WAITING = "WAITING", "Zablokowane / oczekuje"
        COMPLETED = "COMPLETED", "Zrealizowane"
        CANCELLED = "CANCELLED", "Anulowane"

    title = models.CharField("tytuł", max_length=200)
    description = models.TextField("opis", blank=True)
    assigned_unit = models.ForeignKey(
        OrganizationUnit,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="production_tasks",
        verbose_name="przypisana jednostka",
    )
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="individually_assigned_tasks",
        verbose_name="przypisany użytkownik",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_production_tasks",
        verbose_name="autor zadania",
    )
    priority = models.CharField(
        "priorytet", max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    due_date = models.DateField("termin realizacji", null=True, blank=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.NEW)
    production_request = models.ForeignKey(
        ProductionRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="production_tasks",
        verbose_name="powiązane zgłoszenie",
    )
    created_at = models.DateTimeField("utworzono", auto_now_add=True)
    updated_at = models.DateTimeField("zaktualizowano", auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(assigned_unit__isnull=False, assigned_user__isnull=True)
                    | Q(assigned_unit__isnull=True, assigned_user__isnull=False)
                ),
                name="task_has_exactly_one_assignee",
            )
        ]
        verbose_name = "zadanie produkcyjne"
        verbose_name_plural = "zadania produkcyjne"

    def clean(self):
        super().clean()
        if (self.assigned_unit_id is None) == (self.assigned_user_id is None):
            raise ValidationError(
                "Zadanie musi być przypisane do jednej jednostki albo jednej osoby."
            )

    def __str__(self):
        return self.title


class TaskParticipation(models.Model):
    task = models.ForeignKey(
        ProductionTask,
        on_delete=models.CASCADE,
        related_name="participations",
        verbose_name="zadanie",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="task_participations",
        verbose_name="uczestnik",
    )
    started_at = models.DateTimeField("rozpoczęcie", default=timezone.now)
    left_at = models.DateTimeField("opuszczenie", null=True, blank=True)
    leave_note = models.TextField("adnotacja przy opuszczeniu", blank=True)

    class Meta:
        ordering = ["started_at", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "user"],
                condition=Q(left_at__isnull=True),
                name="unique_active_task_participant",
            )
        ]
        verbose_name = "okres uczestnictwa w zadaniu"
        verbose_name_plural = "okresy uczestnictwa w zadaniu"

    def clean(self):
        super().clean()
        if self.left_at and self.started_at and self.left_at < self.started_at:
            raise ValidationError({"left_at": "Czas opuszczenia nie może poprzedzać rozpoczęcia."})


class TaskHistory(models.Model):
    class EventType(models.TextChoices):
        CREATED = "CREATED", "Utworzono"
        STATUS_CHANGED = "STATUS_CHANGED", "Zmieniono status"
        PRIORITY_CHANGED = "PRIORITY_CHANGED", "Zmieniono priorytet"
        ASSIGNED = "ASSIGNED", "Przypisano"
        TRANSFERRED = "TRANSFERRED", "Przekazano"
        COMPLETED = "COMPLETED", "Zakończono"
        PARTICIPANT_STARTED = "PARTICIPANT_STARTED", "Uczestnik rozpoczął"
        PARTICIPANT_LEFT = "PARTICIPANT_LEFT", "Uczestnik opuścił"

    task = models.ForeignKey(
        ProductionTask, on_delete=models.CASCADE, related_name="history", verbose_name="zadanie"
    )
    event_type = models.CharField("zdarzenie", max_length=30, choices=EventType.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="task_history_entries",
        verbose_name="osoba wykonująca",
    )
    old_value = models.TextField("poprzednia wartość", blank=True)
    new_value = models.TextField("nowa wartość", blank=True)
    metadata = models.JSONField("dodatkowe dane", default=dict, blank=True)
    created_at = models.DateTimeField("data i godzina", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "historia zadania"
        verbose_name_plural = "historie zadań"
