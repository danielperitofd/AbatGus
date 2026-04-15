from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from accounts.models import User
from core.mixins import OrganizationManagerRequiredMixin

from .forms import AccessUserSelectForm, UserModuleAccessForm
from .models import Module, UserModuleAccess


class AccessOverviewView(OrganizationManagerRequiredMixin, TemplateView):
    template_name = "access/overview.html"

    def get_available_users(self):
        queryset = User.objects.select_related("organization").order_by("first_name", "username")
        if self.request.user.is_master_global:
            return queryset
        return queryset.filter(organization=self.request.current_organization)

    def get_target_user(self):
        user_id = self.request.GET.get("user") or self.request.POST.get("user_id")
        queryset = self.get_available_users()
        return queryset.filter(pk=user_id).first() if user_id else queryset.first()

    def get_modules(self):
        return Module.objects.select_related("parent").filter(is_active=True).order_by("parent__name", "name")

    def get_access_map(self, user):
        if not user:
            return {}
        return {access.module_id: access for access in UserModuleAccess.objects.filter(user=user)}

    def post(self, request, *args, **kwargs):
        target_user = self.get_target_user()
        modules = list(self.get_modules())
        if not target_user:
            messages.error(request, _("Selecione um usuario para editar os acessos."))
            return redirect("access:overview")
        form = UserModuleAccessForm(request.POST, modules=modules, access_map=self.get_access_map(target_user))
        if form.is_valid():
            form.save(target_user, modules)
            messages.success(request, _("Acessos atualizados para %(user)s.") % {"user": target_user.display_name})
            return redirect(f'{reverse("access:overview")}?user={target_user.pk}')
        return self.render_to_response(self.get_context_data(form=form, target_user=target_user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = kwargs.get("target_user") or self.get_target_user()
        modules = list(self.get_modules())
        access_map = self.get_access_map(target_user)
        grouped_modules = {}
        for module in modules:
            group = module.parent.name if module.parent else _("Geral")
            grouped_modules.setdefault(group, []).append(
                {
                    "module": module,
                    "enabled": access_map.get(module.id).can_view if access_map.get(module.id) else False,
                }
            )

        context.update(
            {
                "page_title": _("Gestao de acessos"),
                "page_description": _("Selecione um usuario e ative ou desative as telas que ele podera acessar."),
                "user_form": AccessUserSelectForm(
                    initial={"user": target_user.pk if target_user else None},
                    user_queryset=self.get_available_users(),
                ),
                "form": kwargs.get("form") or UserModuleAccessForm(
                    initial={"user_id": target_user.pk if target_user else None},
                    modules=modules,
                    access_map=access_map,
                ),
                "target_user": target_user,
                "grouped_modules": grouped_modules,
            }
        )
        return context
