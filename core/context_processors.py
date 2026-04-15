from django.utils.translation import gettext as _

from core.navigation import default_breadcrumbs
from organizations.models import Organization


def app_shell(request):
    current_org = getattr(request, "current_organization", None)
    user = getattr(request, "user", None)
    breadcrumbs = default_breadcrumbs(request)
    current_page_title = breadcrumbs[-1]["label"] if breadcrumbs else _("Painel operacional")
    return {
        "current_organization": current_org,
        "breadcrumbs": breadcrumbs,
        "page_title_context": current_page_title,
        "page_subtitle_context": _("Controle financeiro, produtivo e sanitário em uma única operação."),
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
