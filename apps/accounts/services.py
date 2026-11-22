from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import OrganizationUnit, UserMembership


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
