import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.requests.models import ProductionRequest, RequestItem


@pytest.fixture
def requester(db):
    return User.objects.create_user(
        username="office-requester",
        password="Office-password-2026",
        worker_type=User.WorkerType.OFFICE,
    )


@pytest.fixture
def production_user(db):
    return User.objects.create_user(
        username="production-viewer",
        password="Production-password-2026",
        worker_type=User.WorkerType.PRODUCTION,
    )


def make_request(author, *, status, erp_index):
    request = ProductionRequest.objects.create(
        author=author,
        request_type=ProductionRequest.RequestType.INDEX_ORDER,
        status=status,
    )
    RequestItem.objects.create(production_request=request, erp_index=erp_index)
    return request


@pytest.mark.django_db
def test_production_user_sees_open_requests_from_other_users(
    client, requester, production_user
):
    make_request(
        requester,
        status=ProductionRequest.Status.NEW,
        erp_index="VISIBLE-OPEN-01",
    )
    client.force_login(production_user)

    response = client.get(reverse("requests:list"), {"tab": "open"})

    assert response.status_code == 200
    assert b"VISIBLE-OPEN-01" in response.content
    assert b"office-requester" in response.content


@pytest.mark.django_db
def test_erp_search_works_in_open_and_closed_tabs(client, requester, production_user):
    make_request(
        requester,
        status=ProductionRequest.Status.IN_PROGRESS,
        erp_index="ACTIVE-MATERIAL-42",
    )
    make_request(
        requester,
        status=ProductionRequest.Status.COMPLETED,
        erp_index="DONE-MATERIAL-88",
    )
    client.force_login(production_user)

    open_response = client.get(
        reverse("requests:list"), {"tab": "open", "q": "ACTIVE-MATERIAL"}
    )
    closed_response = client.get(
        reverse("requests:list"), {"tab": "closed", "q": "DONE-MATERIAL"}
    )

    assert b"ACTIVE-MATERIAL-42" in open_response.content
    assert b"DONE-MATERIAL-88" not in open_response.content
    assert b"DONE-MATERIAL-88" in closed_response.content
    assert b"ACTIVE-MATERIAL-42" not in closed_response.content


@pytest.mark.django_db
def test_cancelled_request_is_in_the_closed_history_tab(client, requester, production_user):
    make_request(
        requester,
        status=ProductionRequest.Status.CANCELLED,
        erp_index="CANCELLED-01",
    )
    client.force_login(production_user)

    response = client.get(reverse("requests:list"), {"tab": "closed"})

    assert b"CANCELLED-01" in response.content


@pytest.mark.django_db
def test_htmx_search_returns_only_results_fragment(client, requester, production_user):
    make_request(
        requester,
        status=ProductionRequest.Status.NEW,
        erp_index="HTMX-INDEX-01",
    )
    client.force_login(production_user)

    response = client.get(
        reverse("requests:list"),
        {"tab": "open", "q": "HTMX"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b"id=\"request-results\"" in response.content
    assert b"<html" not in response.content
    assert b"HTMX-INDEX-01" in response.content
