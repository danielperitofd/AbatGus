from django.views.generic import TemplateView

from core.mixins import OrganizationManagerRequiredMixin


class ReportsHubView(OrganizationManagerRequiredMixin, TemplateView):
    template_name = "reports/hub.html"
