from django.urls import path

from apps.requests import views

app_name = "requests"
urlpatterns = [
    path("requests/", views.request_list, name="list"),
    path("requests/new/", views.request_create, name="create"),
    path("requests/items/add/", views.request_item_add, name="item-add"),
]
