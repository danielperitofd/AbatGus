from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import MasterGlobalRequiredMixin

from .forms import OrganizationForm
from .models import Organization


class OrganizationListView(MasterGlobalRequiredMixin, ListView):
    model = Organization
    template_name = "organizations/organization_list.html"
    context_object_name = "organizations"


class OrganizationCreateView(MasterGlobalRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("organizations:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nova organização"
        context["page_description"] = "Cadastre uma nova operação no ecossistema AbatGus."
        return context


class OrganizationUpdateView(MasterGlobalRequiredMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("organizations:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar organização"
        context["page_description"] = "Atualize os dados visuais e institucionais."
        return context
