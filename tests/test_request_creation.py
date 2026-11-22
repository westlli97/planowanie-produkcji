import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.requests.models import ProductionRequest, RequestItem


def request_payload(request_type, priority, items):
    payload = {
        "request_type": request_type,
        "priority": priority,
        "due_date": "",
        "erp_reference_number": "",
        "items-TOTAL_FORMS": str(len(items)),
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",
    }
    for index, item in enumerate(items):
        for field in ("erp_index", "quantity", "unit", "comment"):
            payload[f"items-{index}-{field}"] = item.get(field, "")
    return payload


@pytest.fixture
def requester(db):
    return User.objects.create_user(
        username="new-requester",
        password="Request-password-2026",
        worker_type=User.WorkerType.OFFICE,
    )


@pytest.mark.django_db
def test_create_request_with_one_item_and_optional_quantity_and_unit(client, requester):
    client.force_login(requester)
    payload = request_payload(
        ProductionRequest.RequestType.INDEX_ORDER,
        ProductionRequest.Priority.URGENT,
        [{"erp_index": "IDX-101", "comment": "Pierwszy komentarz"}],
    )

    response = client.post(reverse("requests:create"), payload)

    assert response.status_code == 302
    request = ProductionRequest.objects.get()
    item = RequestItem.objects.get(production_request=request)
    assert request.author == requester
    assert request.priority == ProductionRequest.Priority.URGENT
    assert item.erp_index == "IDX-101"
    assert item.quantity is None
    assert item.unit == ""
    assert item.comment == "Pierwszy komentarz"
    assert request.priority_history.get().new_priority == ProductionRequest.Priority.URGENT


@pytest.mark.django_db
def test_create_request_with_three_independent_items_and_comments(client, requester):
    client.force_login(requester)
    payload = request_payload(
        ProductionRequest.RequestType.INDEX_ORDER,
        ProductionRequest.Priority.NORMAL,
        [
            {"erp_index": "IDX-201", "comment": "Komentarz jeden"},
            {"erp_index": "IDX-202", "comment": "Komentarz dwa"},
            {"erp_index": "IDX-203", "comment": "Komentarz trzy"},
        ],
    )

    response = client.post(reverse("requests:create"), payload)

    assert response.status_code == 302
    items = list(RequestItem.objects.order_by("pk"))
    assert [item.erp_index for item in items] == ["IDX-201", "IDX-202", "IDX-203"]
    assert [item.comment for item in items] == [
        "Komentarz jeden",
        "Komentarz dwa",
        "Komentarz trzy",
    ]


@pytest.mark.django_db
def test_other_request_can_be_created_without_erp_index(client, requester):
    client.force_login(requester)
    payload = request_payload(
        ProductionRequest.RequestType.OTHER,
        ProductionRequest.Priority.NORMAL,
        [{"comment": "Awaria urządzenia"}],
    )

    response = client.post(reverse("requests:create"), payload)

    assert response.status_code == 302
    assert RequestItem.objects.get().erp_index == ""


def test_htmx_adds_a_new_independent_item_row(client, requester):
    client.force_login(requester)

    response = client.get(reverse("requests:item-add"), {"index": 1})

    assert response.status_code == 200
    assert b"items-1-erp_index" in response.content
    assert b'value="2" id="id_items-TOTAL_FORMS" hx-swap-oob="true"' in response.content


@pytest.mark.django_db
def test_index_order_requires_index_for_each_filled_item(client, requester):
    client.force_login(requester)
    payload = request_payload(
        ProductionRequest.RequestType.INDEX_ORDER,
        ProductionRequest.Priority.NORMAL,
        [{"comment": "Pozycja bez indeksu"}],
    )

    response = client.post(reverse("requests:create"), payload)

    assert response.status_code == 200
    assert not ProductionRequest.objects.exists()
    assert "Każda pozycja zamówienia indeksów" in response.content.decode()
