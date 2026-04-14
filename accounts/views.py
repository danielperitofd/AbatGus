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
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("accounts:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_master_global:
            form.fields["organization"].queryset = form.fields["organization"].queryset.filter(
                pk=self.request.current_organization.pk
            )
            form.fields["organization"].initial = self.request.current_organization
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Novo usuário"
        context["page_description"] = "Cadastre gestores e usuários auxiliares com vínculo à organização."
        return context


class UserUpdateView(OrganizationManagerRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("accounts:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_master_global:
            form.fields["organization"].queryset = form.fields["organization"].queryset.filter(
                pk=self.request.current_organization.pk
            )
        return form

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_master_global:
            return queryset
        return queryset.filter(organization=self.request.current_organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar usuário"
        context["page_description"] = "Ajuste permissões operacionais e dados de acesso."
        return context
