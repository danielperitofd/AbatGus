from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from collections import defaultdict

from core.formatting import month_label
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
    MEAT_COLORS = ["#8A2E1E", "#E3B04B", "#314E52", "#7C8C3B", "#C96A4A", "#11212D", "#D9863B"]
    SEMAPHORE_COLORS = ["#1B8A5A", "#E3B04B", "#C13C37"]
    RANGE_OPTIONS = {
        "monthly": {"label": "Mensal", "months": 2},
        "quarterly": {"label": "Trimestral", "months": 3},
        "semiannual": {"label": "Semestral", "months": 6},
        "annual": {"label": "Anual", "months": 12},
    }

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

        selected_range = self.request.GET.get("range", "monthly")
        if selected_range not in self.RANGE_OPTIONS:
            selected_range = "monthly"

        weekly_income = self.filter_month_period_queryset(
            weekly_income, "reference_year", "reference_month", selected_range
        )
        meat_entries = self.filter_month_period_queryset(
            meat_entries, "reference_year", "reference_month", selected_range
        )
        residue_entries = self.filter_date_period_queryset(
            residue_entries, "collected_on", selected_range
        )
        indemnities = self.filter_date_period_queryset(
            indemnities, "occurred_on", selected_range
        )

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
                "operational_panels": self.build_operational_panels(
                    income_summary,
                    meat_summary,
                    residue_summary,
                    indemnity_summary,
                ),
                "dashboard_ranges": [
                    {"value": value, "label": config["label"]}
                    for value, config in self.RANGE_OPTIONS.items()
                ],
                "selected_dashboard_range": selected_range,
            }
        )
        return context

    def get_period_window(self, anchor, selected_range):
        months = self.RANGE_OPTIONS[selected_range]["months"] - 1
        year = anchor.year
        month = anchor.month - months
        while month <= 0:
            month += 12
            year -= 1
        start_date = date(year, month, 1)
        return year, month, start_date

    def filter_month_period_queryset(self, queryset, year_field, month_field, selected_range):
        latest = queryset.order_by(f"-{year_field}", f"-{month_field}").first()
        if not latest:
            return queryset
        anchor = date(getattr(latest, year_field), getattr(latest, month_field), 1)
        start_year, start_month, _ = self.get_period_window(anchor, selected_range)
        return queryset.filter(
            Q(**{f"{year_field}__gt": start_year})
            | Q(**{year_field: start_year, f"{month_field}__gte": start_month})
        )

    def filter_date_period_queryset(self, queryset, field_name, selected_range):
        latest = queryset.order_by(f"-{field_name}").first()
        if not latest:
            return queryset
        anchor = getattr(latest, field_name).replace(day=1)
        _, _, start_date = self.get_period_window(anchor, selected_range)
        return queryset.filter(**{f"{field_name}__gte": start_date})

    def build_income_chart(self, weekly_income):
        series = defaultdict(float)
        for entry in weekly_income.order_by("reference_year", "reference_month", "week_number")[:100]:
            label = f"{month_label(entry.reference_month)} / {entry.reference_year}"
            series[label] += float(entry.calculated_total)
        labels = list(series.keys())
        values = list(series.values())
        return {
            "labels": labels,
            "values": values,
            "items": [{"label": label, "value": value, "color": "#8A2E1E"} for label, value in zip(labels, values)],
        }

    def build_meat_chart(self, meat_entries):
        series = defaultdict(float)
        for entry in meat_entries.select_related("category")[:100]:
            series[entry.category.name] += float(entry.revenue_amount)
        labels = list(series.keys())
        values = list(series.values())
        colors = self.MEAT_COLORS[: len(labels)]
        return {
            "labels": labels,
            "values": values,
            "colors": colors,
            "items": [{"label": label, "value": value, "color": color} for label, value, color in zip(labels, values, colors)],
        }

    def build_semaphore_chart(self, context):
        labels = ["Verde", "Amarelo", "Vermelho"]
        values = [
            context["income_summary"]["success"] + context["meat_summary"]["success"] + context["residue_summary"]["success"] + context["indemnity_summary"]["success"],
            context["income_summary"]["warning"] + context["meat_summary"]["warning"] + context["residue_summary"]["warning"] + context["indemnity_summary"]["warning"],
            context["income_summary"]["danger"] + context["meat_summary"]["danger"] + context["residue_summary"]["danger"] + context["indemnity_summary"]["danger"],
        ]
        return {
            "labels": labels,
            "values": values,
            "colors": self.SEMAPHORE_COLORS,
            "items": [{"label": label, "value": value, "color": color} for label, value, color in zip(labels, values, self.SEMAPHORE_COLORS)],
        }

    def build_operational_panels(self, income_summary, meat_summary, residue_summary, indemnity_summary):
        modules = [
            ("Fontes de renda", income_summary),
            ("Carnes", meat_summary),
            ("Residuos", residue_summary),
            ("Indenizacoes", indemnity_summary),
        ]
        panels = []
        for label, summary in modules:
            panels.append(
                {
                    "label": label,
                    "total": summary["success"] + summary["warning"] + summary["danger"],
                    "items": [
                        {"label": "Verdes", "value": summary["success"], "color": "#1B8A5A"},
                        {"label": "Amarelos", "value": summary["warning"], "color": "#E3B04B"},
                        {"label": "Vermelhos", "value": summary["danger"], "color": "#C13C37"},
                    ],
                }
            )
        return panels


class SwitchOrganizationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_master_global:
            messages.error(request, "Apenas o master global pode trocar a organização.")
            return redirect("core:dashboard")

        organization = get_object_or_404(Organization, pk=kwargs["pk"], is_active=True)
        request.session["current_organization_id"] = organization.pk
        messages.success(request, f"Contexto alterado para {organization.name}.")
        return redirect(request.POST.get("next") or reverse_lazy("core:dashboard"))
