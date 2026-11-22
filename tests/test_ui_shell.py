import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_ui_preview_renders_base_and_shared_components(client, db):
    user = User.objects.create_user(
        username="preview-user", password="test-password", worker_type=User.WorkerType.OFFICE
    )
    client.force_login(user)
    response = client.get("/ui-preview/")

    assert response.status_code == 200
    assert b"<html lang=\"pl\">" in response.content
    assert b"Biuro \xe2\x80\x93 Produkcja" in response.content
    assert b"Nawigacja mobilna" in response.content
    assert b"modal-container" in response.content
    assert b"toast-container" in response.content
    assert b"Nowe" in response.content
    assert b"Priorytet: Wysoki" in response.content
