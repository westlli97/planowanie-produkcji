from django.urls import path

from apps.production import views

app_name = "production"
urlpatterns = [
    path("tasks/", views.task_list, name="task-list"),
    path("tasks/new/", views.task_create, name="task-create"),
    path("tasks/<int:task_id>/transfer/", views.task_transfer, name="task-transfer"),
]
