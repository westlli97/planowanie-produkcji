from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ProductionRequest(models.Model):
    class RequestType(models.TextChoices):
        INDEX_ORDER = "INDEX_ORDER", "Zamawianie indeksów"
        OTHER = "OTHER", "Inne zgłoszenie"

    class Priority(models.TextChoices):
        NORMAL = "NORMAL", "Normalny"
        URGENT = "URGENT", "Pilny"

    class Status(models.TextChoices):
        NEW = "NEW", "Nowe"
        IN_PROGRESS = "IN_PROGRESS", "W trakcie"
        WAITING = "WAITING", "Oczekuje"
        COMPLETED = "COMPLETED", "Zrealizowane"
        CANCELLED = "CANCELLED", "Anulowane"

    request_type = models.CharField(
        "rodzaj zgłoszenia", max_length=20, choices=RequestType.choices
    )
    priority = models.CharField(
        "priorytet", max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    due_date = models.DateField("termin realizacji", null=True, blank=True)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.NEW
    )
    erp_reference_number = models.CharField(
        "numer referencyjny ERP", max_length=100, blank=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="production_requests",
        verbose_name="autor",
    )
    created_at = models.DateTimeField("utworzono", auto_now_add=True)
    updated_at = models.DateTimeField("zaktualizowano", auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "zgłoszenie"
        verbose_name_plural = "zgłoszenia"

    def __str__(self):
        return f"Zgłoszenie #{self.pk}"


class RequestItem(models.Model):
    class Unit(models.TextChoices):
        PCS = "PCS", "szt."
        METERS = "METERS", "metry"

    production_request = models.ForeignKey(
        ProductionRequest,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="zgłoszenie",
    )
    erp_index = models.CharField("indeks ERP", max_length=100, blank=True)
    quantity = models.DecimalField(
        "ilość", max_digits=12, decimal_places=3, null=True, blank=True
    )
    unit = models.CharField(
        "jednostka miary", max_length=10, choices=Unit.choices, blank=True
    )
    comment = models.TextField("komentarz", blank=True)

    class Meta:
        ordering = ["pk"]
        verbose_name = "pozycja zgłoszenia"
        verbose_name_plural = "pozycje zgłoszenia"

    def clean(self):
        super().clean()
        if (
            self.production_request_id
            and self.production_request.request_type == ProductionRequest.RequestType.INDEX_ORDER
            and not self.erp_index.strip()
        ):
            raise ValidationError({"erp_index": "Podaj indeks ERP dla zamawiania indeksów."})

    def __str__(self):
        return self.erp_index or f"Pozycja zgłoszenia #{self.production_request_id}"


class RequestHistory(models.Model):
    production_request = models.ForeignKey(
        ProductionRequest,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="zgłoszenie",
    )
    field_name = models.CharField("zmienione pole", max_length=50)
    old_value = models.TextField("poprzednia wartość", blank=True)
    new_value = models.TextField("nowa wartość", blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="request_history_entries",
        verbose_name="osoba wykonująca",
    )
    created_at = models.DateTimeField("data i godzina", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "historia zgłoszenia"
        verbose_name_plural = "historie zgłoszeń"


class PriorityHistory(models.Model):
    production_request = models.ForeignKey(
        ProductionRequest,
        on_delete=models.CASCADE,
        related_name="priority_history",
        verbose_name="zgłoszenie",
    )
    old_priority = models.CharField(
        "poprzedni priorytet",
        max_length=10,
        choices=ProductionRequest.Priority.choices,
        blank=True,
    )
    new_priority = models.CharField(
        "nowy priorytet", max_length=10, choices=ProductionRequest.Priority.choices
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="priority_history_entries",
        verbose_name="osoba wykonująca",
    )
    created_at = models.DateTimeField("data i godzina", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "historia priorytetu"
        verbose_name_plural = "historie priorytetów"
