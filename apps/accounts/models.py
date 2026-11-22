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


class AppPermission(models.Model):
    code = models.SlugField("kod", max_length=100, unique=True)
    name = models.CharField("nazwa", max_length=150)
    description = models.TextField("opis", blank=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "uprawnienie aplikacji"
        verbose_name_plural = "uprawnienia aplikacji"

    def __str__(self):
        return self.name


class JobFunction(models.Model):
    name = models.CharField("nazwa funkcji", max_length=120, unique=True)
    permissions = models.ManyToManyField(
        AppPermission, blank=True, related_name="job_functions", verbose_name="uprawnienia domyślne"
    )
    is_administrator = models.BooleanField("pełny dostęp administratora", default=False)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "funkcja"
        verbose_name_plural = "funkcje"

    def __str__(self):
        return self.name


class UserFunction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_functions"
    )
    job_function = models.ForeignKey(
        JobFunction, on_delete=models.CASCADE, related_name="users"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "job_function"], name="unique_user_job_function"
            )
        ]
        verbose_name = "funkcja użytkownika"
        verbose_name_plural = "funkcje użytkowników"


class PermissionOverride(models.Model):
    permission = models.ForeignKey(
        AppPermission, on_delete=models.CASCADE, related_name="overrides"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="permission_overrides",
    )
    group = models.ForeignKey(
        "auth.Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="permission_overrides",
    )
    allowed = models.BooleanField("zezwól", default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, group__isnull=True)
                    | models.Q(user__isnull=True, group__isnull=False)
                ),
                name="permission_override_has_one_target",
            ),
            models.UniqueConstraint(
                fields=["user", "permission"],
                condition=models.Q(user__isnull=False),
                name="unique_user_permission_override",
            ),
            models.UniqueConstraint(
                fields=["group", "permission"],
                condition=models.Q(group__isnull=False),
                name="unique_group_permission_override",
            ),
        ]
        verbose_name = "nadpisanie uprawnienia"
        verbose_name_plural = "nadpisania uprawnień"


class WorkerTypePermission(models.Model):
    worker_type = models.CharField("typ pracownika", max_length=12, choices=User.WorkerType.choices)
    permission = models.ForeignKey(
        AppPermission, on_delete=models.CASCADE, related_name="worker_type_defaults"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["worker_type", "permission"], name="unique_worker_type_permission"
            )
        ]
        verbose_name = "domyślne uprawnienie typu pracownika"
        verbose_name_plural = "domyślne uprawnienia typu pracownika"
