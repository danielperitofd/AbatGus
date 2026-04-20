from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import OrganizationManagerRequiredMixin

from .forms import LoginForm, UserForm
from .models import User


class AbatGusLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class AbatGusLogoutView(LogoutView):
    pass


class UserListView(OrganizationManagerRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = User.objects.select_related("organization").order_by("first_name", "username")
        user = self.request.user
        if user.is_master_global:
            return queryset
        return queryset.filter(organization=self.request.current_organization)


class UserCreateView(OrganizationManagerRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:list")

    def get_effective_organization(self):
        return getattr(self.request, "current_organization", None) or getattr(self.request.user, "organization", None)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        current_organization = self.get_effective_organization()
        if not self.request.user.is_master_global and current_organization:
            form.fields["organization"].queryset = form.fields["organization"].queryset.filter(
                pk=current_organization.pk
            )
            form.fields["organization"].initial = current_organization
        elif not self.request.user.is_master_global:
            form.fields["organization"].queryset = form.fields["organization"].queryset.none()
            form.fields["organization"].required = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Novo usuário"
        context["page_description"] = "Cadastre gestores e usuários auxiliares com vínculo à organização."
        context["form_variant"] = "user"
        return context


class UserUpdateView(OrganizationManagerRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:list")

    def get_effective_organization(self):
        return getattr(self.request, "current_organization", None) or getattr(self.request.user, "organization", None)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        current_organization = self.get_effective_organization()
        if not self.request.user.is_master_global and current_organization:
            form.fields["organization"].queryset = form.fields["organization"].queryset.filter(
                pk=current_organization.pk
            )
        elif not self.request.user.is_master_global:
            instance_org_id = getattr(self.object, "organization_id", None)
            if instance_org_id:
                form.fields["organization"].queryset = form.fields["organization"].queryset.filter(pk=instance_org_id)
            else:
                form.fields["organization"].queryset = form.fields["organization"].queryset.none()
                form.fields["organization"].required = False
        return form

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_master_global:
            return queryset
        current_organization = self.get_effective_organization()
        if current_organization:
            return queryset.filter(organization=current_organization)
        return queryset.filter(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar usuário"
        context["page_description"] = "Ajuste permissões operacionais e dados de acesso."
        context["form_variant"] = "user"
        return context
