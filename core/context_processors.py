from organizations.models import Organization


def app_shell(request):
    current_org = getattr(request, "current_organization", None)
    user = getattr(request, "user", None)
    return {
        "current_organization": current_org,
        "organizations": Organization.objects.filter(is_active=True).order_by("name")
        if user and user.is_authenticated and getattr(user, "is_master_global", False)
        else [],
        "can_see_admin_tools": bool(
            user and user.is_authenticated and getattr(user, "is_master_global", False)
        ),
        "can_see_settings": bool(
            user
            and user.is_authenticated
            and (
                getattr(user, "is_master_global", False)
                or getattr(user, "is_organization_manager", False)
            )
        ),
    }
