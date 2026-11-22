import pytest


@pytest.mark.django_db
def test_ui_preview_renders_base_and_shared_components(client):
    response = client.get("/ui-preview/")

    assert response.status_code == 200
    assert b"<html lang=\"pl\">" in response.content
    assert b"Biuro \xe2\x80\x93 Produkcja" in response.content
    assert b"Nawigacja mobilna" in response.content
    assert b"modal-container" in response.content
    assert b"toast-container" in response.content
    assert b"Nowe" in response.content
    assert b"Priorytet: Wysoki" in response.content
