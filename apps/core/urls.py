from django.urls import path

from apps.core import views

app_name = "core"
urlpatterns = [
    path("ui-preview/", views.ui_preview, name="ui-preview"),
    path("ui-preview/modal/", views.modal_preview, name="modal-preview"),
]
