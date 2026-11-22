import pytest
from django.urls import reverse

from apps.accounts.models import OrganizationUnit, User, UserMembership
from apps.accounts.services import assign_membership


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="structure-admin",
        password="Admin-password-2026",
        worker_type=User.WorkerType.OFFICE,
        is_staff=True,
    )


@pytest.mark.django_db
def test_user_can_belong_to_multiple_units_with_one_primary():
    user = User.objects.create_user(
        username="multi-unit",
        password="Worker-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )
    office = OrganizationUnit.objects.create(name="Biuro")
    production = OrganizationUnit.objects.create(name="Produkcja")
    packing = OrganizationUnit.objects.create(name="Pakowalnia", parent=production)

    assign_membership(user=user, organization_unit=office, is_primary=True)
    assign_membership(user=user, organization_unit=packing, is_primary=False)
    assign_membership(user=user, organization_unit=production, is_primary=True)

    memberships = list(UserMembership.objects.filter(user=user).order_by("organization_unit__name"))
    assert len(memberships) == 3
    assert {membership.organization_unit_id for membership in memberships} == {
        office.pk,
        packing.pk,
        production.pk,
    }
    primaries = [
        membership.organization_unit for membership in memberships if membership.is_primary
    ]
    assert primaries == [production]
    assert packing.parent == production


def test_organization_panel_requires_staff_user(client, admin_user):
    response = client.get(reverse("accounts:organization-panel"))
    assert response.status_code == 302

    client.force_login(admin_user)
    response = client.get(reverse("accounts:organization-panel"))

    assert response.status_code == 200
    assert b"Struktura organizacyjna" in response.content
