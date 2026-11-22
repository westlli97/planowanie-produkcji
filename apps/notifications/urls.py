from django.urls import path

from apps.notifications import views

app_name = "notifications"
urlpatterns = [
    path("notifications/unread/", views.unread_list, name="unread-list"),
]
