from django.urls import path

from apps.requests import views

app_name = "requests"
urlpatterns = [
    path("requests/<int:request_id>/", views.request_detail, name="detail"),
    path(
        "requests/<int:request_id>/status/",
        views.request_status_update,
        name="status-update",
    ),
    path(
        "requests/<int:request_id>/priority/",
        views.request_priority_update,
        name="priority-update",
    ),
    path(
        "requests/<int:request_id>/due-date/",
        views.request_due_date_update,
        name="due-date-update",
    ),
    path(
        "requests/<int:request_id>/erp-reference/",
        views.request_erp_reference_update,
        name="erp-reference-update",
    ),
    path("requests/", views.request_list, name="list"),
    path("requests/new/", views.request_create, name="create"),
    path("requests/items/add/", views.request_item_add, name="item-add"),
]
