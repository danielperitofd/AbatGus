from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def _safe_reverse(name, **kwargs):
    try:
        return reverse(name, kwargs=kwargs or None)
    except Exception:
        return None


def default_breadcrumbs(request):
    match = getattr(request, "resolver_match", None)
    crumbs = [{"label": _("Início"), "url": _safe_reverse("core:dashboard")}]
    if not match:
        return crumbs

    namespace = match.namespace
    url_name = match.url_name or ""

    if namespace == "operations":
        crumbs.append({"label": _("Operações"), "url": None})
        if url_name.startswith("income-item"):
            crumbs.append({"label": _("Cadastros"), "url": None})
            crumbs.append({"label": _("Fontes de renda"), "url": _safe_reverse("operations:income-item-list")})
        elif url_name.startswith("meat-category"):
            crumbs.append({"label": _("Cadastros"), "url": None})
            crumbs.append({"label": _("Carnes"), "url": _safe_reverse("operations:meat-category-list")})
        elif url_name.startswith("residue-category"):
            crumbs.append({"label": _("Cadastros"), "url": None})
            crumbs.append({"label": _("Resíduos"), "url": _safe_reverse("operations:residue-category-list")})
        elif url_name.startswith("income"):
            crumbs.append({"label": _("Fontes de renda"), "url": _safe_reverse("operations:income-list")})
        elif url_name.startswith("meat"):
            crumbs.append({"label": _("Carnes"), "url": _safe_reverse("operations:meat-list")})
        elif url_name.startswith("residue"):
            crumbs.append({"label": _("Resíduos"), "url": _safe_reverse("operations:residue-list")})
        elif url_name.startswith("indemnity"):
            crumbs.append({"label": _("Indenizações"), "url": _safe_reverse("operations:indemnity-list")})

    elif namespace == "accounts":
        crumbs.append({"label": _("Contas"), "url": None})
        crumbs.append({"label": _("Usuários"), "url": _safe_reverse("accounts:list")})
    elif namespace == "access":
        crumbs.append({"label": _("Acessos"), "url": _safe_reverse("access:overview")})
    elif namespace == "organizations":
        crumbs.append({"label": _("Admin Tools"), "url": None})
        crumbs.append({"label": _("Organizações"), "url": _safe_reverse("organizations:list")})
    elif namespace == "reports":
        crumbs.append({"label": _("Relatórios"), "url": _safe_reverse("reports:hub")})

    action_map = {
        "create": _("Novo"),
        "update": _("Editar"),
        "detail": _("Visualizar"),
        "delete": _("Excluir"),
        "import": _("Importar"),
    }
    for key, label in action_map.items():
        if url_name.endswith(key):
            crumbs.append({"label": label, "url": None})
            break
    return crumbs
