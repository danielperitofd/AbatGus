from django.views.generic import TemplateView

from core.mixins import OrganizationManagerRequiredMixin

from .models import Module


class AccessOverviewView(OrganizationManagerRequiredMixin, TemplateView):
    template_name = "access/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modules"] = Module.objects.select_related("parent").order_by("parent__name", "name")
        return context
