from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class OrganizationScopedMixin(LoginRequiredMixin):
    organization_field = "organization"

    def get_organization(self):
        org = getattr(self.request, "current_organization", None)
        if not org and not self.request.user.is_master_global:
            raise PermissionDenied("Nenhuma organização ativa foi selecionada.")
        return org

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_master_global:
            return queryset
        return queryset.filter(**{self.organization_field: self.get_organization()})

    def get_catalog_queryset(self, queryset, organization_field="organization"):
        organization = getattr(self.request, "current_organization", None)
        if self.request.user.is_master_global and not organization:
            return queryset
        if organization:
            return queryset.filter(**{organization_field: organization})
        return queryset.none()

    def form_valid(self, form):
        if hasattr(form.instance, self.organization_field + "_id") and not getattr(
            form.instance, self.organization_field + "_id"
        ):
            organization = self.get_organization()
            if organization:
                setattr(form.instance, self.organization_field, organization)
        return super().form_valid(form)


class MasterGlobalRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_master_global


class OrganizationManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_master_global or user.is_organization_manager
        )
