import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="operator",
        password="Good-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )


def test_login_authenticates_user(client, user):
    response = client.post(
        reverse("accounts:login"),
        {"username": "operator", "password": "Good-password-2026"},
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


def test_logout_ends_session(client, user):
    client.force_login(user)

    response = client.post(reverse("accounts:logout"))

    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get("/ui-preview/")

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))

