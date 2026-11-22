from apps.accounts.models import OrganizationUnit


def get_organization_units():
    return OrganizationUnit.objects.select_related("parent").prefetch_related(
        "children", "memberships__user"
    )
