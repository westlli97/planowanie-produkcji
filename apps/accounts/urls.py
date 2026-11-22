from django.contrib.auth import views as auth_views
from django.urls import path

from apps.accounts import operational_views

app_name = "accounts"
urlpatterns = [
    path("organization/", operational_views.organization_panel, name="organization-panel"),
    path(
        "organization/new/",
        operational_views.organization_unit_edit,
        name="organization-unit-create",
    ),
    path(
        "organization/<int:unit_id>/edit/",
        operational_views.organization_unit_edit,
        name="organization-unit-edit",
    ),
    path(
        "organization/<int:unit_id>/toggle/",
        operational_views.organization_unit_toggle,
        name="organization-unit-toggle",
    ),
    path(
        "organization/membership/",
        operational_views.organization_membership_add,
        name="organization-membership-add",
    ),
    path("permissions/", operational_views.permission_panel, name="permission-panel"),
    path("permissions/new/", operational_views.permission_create, name="permission-create"),
    path(
        "permissions/functions/new/",
        operational_views.job_function_edit,
        name="job-function-create",
    ),
    path(
        "permissions/functions/<int:function_id>/edit/",
        operational_views.job_function_edit,
        name="job-function-edit",
    ),
    path(
        "permissions/assign/",
        operational_views.function_assignment_add,
        name="function-assignment-add",
    ),
    path(
        "permissions/override/",
        operational_views.permission_override_add,
        name="permission-override-add",
    ),
    path(
        "permissions/worker-default/",
        operational_views.worker_type_permission_add,
        name="worker-type-permission-add",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="pages/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),
]
