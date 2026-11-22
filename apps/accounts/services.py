from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import (
    AppPermission,
    OrganizationUnit,
    PermissionOverride,
    UserFunction,
    UserMembership,
    WorkerTypePermission,
)


@transaction.atomic
def save_organization_unit(*, unit=None, name, parent=None, is_active=True):
    unit = unit or OrganizationUnit()
    unit.name = name.strip()
    unit.parent = parent
    unit.is_active = is_active
    unit.full_clean()
    unit.save()
    return unit


@transaction.atomic
def set_organization_unit_active(*, unit, is_active):
    unit.is_active = is_active
    unit.save(update_fields=["is_active"])
    return unit


@transaction.atomic
def assign_membership(*, user, organization_unit, is_primary=False):
    if not organization_unit.is_active:
        raise ValidationError("Nie można przypisać użytkownika do nieaktywnej jednostki.")
    if is_primary:
        UserMembership.objects.filter(user=user, is_primary=True).exclude(
            organization_unit=organization_unit
        ).update(is_primary=False)
    membership, _ = UserMembership.objects.get_or_create(
        user=user, organization_unit=organization_unit
    )
    if membership.is_primary != is_primary:
        membership.is_primary = is_primary
        membership.save(update_fields=["is_primary"])
    return membership


@transaction.atomic
def assign_job_function(*, user, job_function):
    assignment, _ = UserFunction.objects.get_or_create(user=user, job_function=job_function)
    return assignment


@transaction.atomic
def set_permission_override(*, permission, allowed, user=None, group=None):
    if (user is None) == (group is None):
        raise ValidationError("Wskaż dokładnie jednego użytkownika albo grupę.")
    override, _ = PermissionOverride.objects.update_or_create(
        permission=permission, user=user, group=group, defaults={"allowed": allowed}
    )
    return override


def has_permission(user, permission_code):
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser or user.is_staff:
        return True

    if user.job_functions.filter(job_function__is_administrator=True).exists():
        return True

    permission = AppPermission.objects.filter(code=permission_code).first()
    if permission is None:
        return False

    user_override = PermissionOverride.objects.filter(
        user=user, permission=permission
    ).values_list("allowed", flat=True).first()
    if user_override is not None:
        return user_override

    group_overrides = PermissionOverride.objects.filter(
        group__in=user.groups.all(), permission=permission
    )
    if group_overrides.filter(allowed=False).exists():
        return False
    if group_overrides.filter(allowed=True).exists():
        return True

    if WorkerTypePermission.objects.filter(
        worker_type=user.worker_type, permission=permission
    ).exists():
        return True
    return user.job_functions.filter(job_function__permissions=permission).exists()
