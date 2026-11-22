import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.accounts.models import (
    AppPermission,
    JobFunction,
    PermissionOverride,
    User,
    UserFunction,
    WorkerTypePermission,
)
from apps.accounts.services import (
    assign_job_function,
    has_permission,
    set_permission_override,
)


@pytest.fixture
def permission(db):
    return AppPermission.objects.create(code="requests.change_due_date", name="Zmień termin")


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="permission-user",
        password="User-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )


@pytest.mark.django_db
def test_permission_inherited_from_job_function(user, permission):
    job_function = JobFunction.objects.create(name="Brygadzista")
    job_function.permissions.add(permission)
    assign_job_function(user=user, job_function=job_function)

    assert has_permission(user, permission.code)


@pytest.mark.django_db
def test_group_and_user_permission_overrides(user, permission):
    job_function = JobFunction.objects.create(name="Kierownik")
    job_function.permissions.add(permission)
    assign_job_function(user=user, job_function=job_function)
    group = Group.objects.create(name="Zespół produkcji")
    user.groups.add(group)

    set_permission_override(permission=permission, group=group, allowed=False)
    user.refresh_from_db()
    assert not has_permission(user, permission.code)

    set_permission_override(permission=permission, user=user, allowed=True)
    assert has_permission(user, permission.code)

    PermissionOverride.objects.filter(user=user, permission=permission).update(allowed=False)
    assert not has_permission(user, permission.code)


@pytest.mark.django_db
def test_group_override_can_grant_permission(user, permission):
    group = Group.objects.create(name="Zespół terminów")
    user.groups.add(group)
    set_permission_override(permission=permission, group=group, allowed=True)

    assert has_permission(user, permission.code)


@pytest.mark.django_db
def test_administrator_function_grants_full_access(user):
    administrator = JobFunction.objects.create(name="Administrator", is_administrator=True)
    UserFunction.objects.create(user=user, job_function=administrator)

    assert has_permission(user, "any.future.permission")


@pytest.mark.django_db
def test_worker_type_defaults_are_inherited(user, permission):
    WorkerTypePermission.objects.create(
        worker_type=User.WorkerType.PRODUCTION,
        permission=permission,
    )

    assert has_permission(user, permission.code)


def test_permission_panel_requires_staff_user(client, db):
    response = client.get(reverse("accounts:permission-panel"))
    assert response.status_code == 302

    administrator = User.objects.create_user(
        username="permission-admin",
        password="Admin-password-2026",
        worker_type=User.WorkerType.OFFICE,
        is_staff=True,
    )
    client.force_login(administrator)
    response = client.get(reverse("accounts:permission-panel"))

    assert response.status_code == 200
    assert b"Funkcje i uprawnienia" in response.content
