from django.urls import path

from apps.production import views

app_name = "production"
urlpatterns = [
    path("tasks/", views.task_list, name="task-list"),
    path("tasks/new/", views.task_create, name="task-create"),
    path("tasks/<int:task_id>/transfer/", views.task_transfer, name="task-transfer"),
    path("tasks/<int:task_id>/join/", views.task_join, name="task-join"),
    path("tasks/<int:task_id>/leave/", views.task_leave, name="task-leave"),
    path(
        "tasks/<int:task_id>/finish-confirmation/",
        views.task_finish_confirmation,
        name="task-finish-confirmation",
    ),
    path("tasks/<int:task_id>/finish/", views.task_finish, name="task-finish"),
    path("tasks/<int:task_id>/", views.task_detail, name="task-detail"),
]
