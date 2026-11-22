from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    class WorkerType(models.TextChoices):
        OFFICE = "OFFICE", "Biuro"
        PRODUCTION = "PRODUCTION", "Produkcja"

    worker_type = models.CharField(
        "typ pracownika",
        max_length=12,
        choices=WorkerType.choices,
    )

    def __str__(self):
        return self.get_full_name() or self.username


class OrganizationUnit(models.Model):
    name = models.CharField("nazwa", max_length=150)
    parent = models.ForeignKey(
        "self",
        verbose_name="jednostka nadrzędna",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    is_active = models.BooleanField("aktywna", default=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "jednostka organizacyjna"
        verbose_name_plural = "jednostki organizacyjne"

    def clean(self):
        super().clean()
        ancestor = self.parent
        while ancestor is not None:
            if self.pk is not None and ancestor.pk == self.pk:
                raise ValidationError({"parent": "Jednostka nie może być swoim własnym przodkiem."})
            ancestor = ancestor.parent

    def __str__(self):
        return self.name


class UserMembership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    organization_unit = models.ForeignKey(
        OrganizationUnit, on_delete=models.PROTECT, related_name="memberships"
    )
    is_primary = models.BooleanField("główna przynależność", default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization_unit"], name="unique_user_organization_membership"
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_primary=True),
                name="unique_primary_membership_per_user",
            ),
        ]
        verbose_name = "przynależność użytkownika"
        verbose_name_plural = "przynależności użytkowników"

    def __str__(self):
        return f"{self.user} – {self.organization_unit}"
