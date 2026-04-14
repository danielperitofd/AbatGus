from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from collections import defaultdict

from organizations.models import Organization
from operations.models import (
    IndemnityRecord,
    MeatProductionEntry,
    ResidueCollection,
    WeeklyIncomeEntry,
)
from operations.services import (
    attach_income_status,
    attach_indemnity_status,
    attach_meat_status,
    attach_residue_status,
    summarize_semaphores,
)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.request.current_organization

        weekly_income = WeeklyIncomeEntry.objects.all()
        meat_entries = MeatProductionEntry.objects.all()
        residue_entries = ResidueCollection.objects.all()
        indemnities = IndemnityRecord.objects.all()

        if organization and not self.request.user.is_master_global:
            weekly_income = weekly_income.filter(organization=organization)
            meat_entries = meat_entries.filter(organization=organization)
            residue_entries = residue_entries.filter(organization=organization)
            indemnities = indemnities.filter(organization=organization)

        recent_incomes = attach_income_status(
            list(
                weekly_income.select_related("item")
                .order_by("-reference_year", "-reference_month", "-week_number")[:6]
            )
        )
        recent_meats = attach_meat_status(
            list(
                meat_entries.select_related("category")
                .order_by("-reference_year", "-reference_month", "-week_number")[:6]
            )
        )
        recent_residues = attach_residue_status(
            list(residue_entries.select_related("category").order_by("-collected_on")[:6]),
            residue_entries,
        )
        recent_indemnities = attach_indemnity_status(list(indemnities.order_by("-occurred_on")[:6]))
        income_summary = summarize_semaphores(attach_income_status(list(weekly_income.select_related("item")[:50])))
        meat_summary = summarize_semaphores(attach_meat_status(list(meat_entries.select_related("category")[:50])))
        residue_summary = summarize_semaphores(
            attach_residue_status(list(residue_entries.select_related("category")[:50]), residue_entries)
        )
        indemnity_summary = summarize_semaphores(attach_indemnity_status(list(indemnities[:50])))

        context.update(
            {
                "income_total": weekly_income.aggregate(total=Sum("quantity"))["total"] or 0,
                "meat_total": meat_entries.aggregate(total=Sum("weight_kg"))["total"] or 0,
                "donation_total": meat_entries.aggregate(total=Sum("donation_kg"))["total"] or 0,
                "residue_total": residue_entries.aggregate(total=Sum("quantity"))["total"] or 0,
                "indemnity_total": indemnities.aggregate(total=Sum("outgoing_amount"))["total"] or 0,
                "recent_incomes": recent_incomes,
                "recent_meats": recent_meats,
                "recent_residues": recent_residues,
                "recent_indemnities": recent_indemnities,
                "income_summary": income_summary,
                "meat_summary": meat_summary,
                "residue_summary": residue_summary,
                "indemnity_summary": indemnity_summary,
                "organizations": Organization.objects.filter(is_active=True).order_by("name"),
                "income_chart": self.build_income_chart(weekly_income),
                "meat_chart": self.build_meat_chart(meat_entries),
                "semaphore_chart": self.build_semaphore_chart(
                    {
                        "income_summary": income_summary,
                        "meat_summary": meat_summary,
                        "residue_summary": residue_summary,
                        "indemnity_summary": indemnity_summary,
                    }
                ),
            }
        )
        return context

    def build_income_chart(self, weekly_income):
        series = defaultdict(float)
        for entry in weekly_income.order_by("reference_year", "reference_month", "week_number")[:100]:
            label = f"{entry.reference_month:02d}/{entry.reference_year}"
            series[label] += float(entry.calculated_total)
        return {"labels": list(series.keys()), "values": list(series.values())}

    def build_meat_chart(self, meat_entries):
        series = defaultdict(float)
        for entry in meat_entries.select_related("category")[:100]:
            series[entry.category.name] += float(entry.revenue_amount)
        return {"labels": list(series.keys()), "values": list(series.values())}

    def build_semaphore_chart(self, context):
        return {
            "labels": ["Verde", "Amarelo", "Vermelho"],
            "values": [
                context["income_summary"]["success"] + context["meat_summary"]["success"] + context["residue_summary"]["success"] + context["indemnity_summary"]["success"],
                context["income_summary"]["warning"] + context["meat_summary"]["warning"] + context["residue_summary"]["warning"] + context["indemnity_summary"]["warning"],
                context["income_summary"]["danger"] + context["meat_summary"]["danger"] + context["residue_summary"]["danger"] + context["indemnity_summary"]["danger"],
            ],
        }


class SwitchOrganizationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_master_global:
            messages.error(request, "Apenas o master global pode trocar a organização.")
            return redirect("core:dashboard")

        organization = get_object_or_404(Organization, pk=kwargs["pk"], is_active=True)
        request.session["current_organization_id"] = organization.pk
        messages.success(request, f"Contexto alterado para {organization.name}.")
        return redirect(request.POST.get("next") or reverse_lazy("core:dashboard"))
