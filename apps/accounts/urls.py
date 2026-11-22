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
