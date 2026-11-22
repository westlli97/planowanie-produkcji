import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.requests.models import ProductionRequest, RequestItem


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username="request-author",
        password="Request-password-2026",
        worker_type=User.WorkerType.OFFICE,
    )


@pytest.mark.django_db
def test_index_order_item_allows_empty_quantity_and_unit(author):
    request = ProductionRequest.objects.create(
        author=author, request_type=ProductionRequest.RequestType.INDEX_ORDER
    )
    item = RequestItem(
        production_request=request,
        erp_index="ERP-123",
        quantity=None,
        unit="",
    )

    item.full_clean()


@pytest.mark.django_db
def test_other_request_does_not_require_erp_index(author):
    request = ProductionRequest.objects.create(
        author=author, request_type=ProductionRequest.RequestType.OTHER
    )
    item = RequestItem(production_request=request, erp_index="")

    item.full_clean()


@pytest.mark.django_db
def test_index_order_requires_erp_index(author):
    request = ProductionRequest.objects.create(
        author=author, request_type=ProductionRequest.RequestType.INDEX_ORDER
    )
    item = RequestItem(production_request=request, erp_index="   ")

    with pytest.raises(ValidationError, match="Podaj indeks ERP"):
        item.full_clean()
