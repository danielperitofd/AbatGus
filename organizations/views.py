from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from core.mixins import MasterGlobalRequiredMixin
from operations.models import (
    IncomeItem,
    IndemnityLookupValue,
    IndemnityRecord,
    MeatCategory,
    MeatProductionEntry,
    ResidueCategory,
    ResidueCollection,
    WeeklyIncomeEntry,
)
from operations.services import sync_indemnity_lookup_values

from .forms import OrganizationForm
from .models import Organization


def _get_target_organization(request):
    return getattr(request, "current_organization", None) or Organization.objects.filter(is_active=True).order_by("name").first()


def _populate_income_test_data(organization):
    items = [
        ("Boi", "UNIT", Decimal("36068.00")),
        ("Porco", "UNIT", Decimal("11020.00")),
        ("Carnes", "KG", Decimal("743.88")),
        ("Sebo", "UNIT", Decimal("920.00")),
        ("Livro", "UNIT", Decimal("580.00")),
        ("Vergalho", "UNIT", Decimal("485.00")),
        ("Pele", "UNIT", Decimal("300.00")),
        ("Fretes", "SERVICE", Decimal("350.00")),
        ("Frete Sao Joao", "SERVICE", Decimal("350.00")),
        ("Frete Palmerina", "SERVICE", Decimal("580.00")),
    ]
    for index, (name, unit, price) in enumerate(items, start=1):
        item, _ = IncomeItem.objects.get_or_create(
            organization=organization,
            name=name,
            defaults={"unit": unit, "default_price": price, "is_active": True},
        )
        WeeklyIncomeEntry.objects.get_or_create(
            organization=organization,
            item=item,
            reference_year=2026,
            reference_month=4,
            week_number=min(index, 5),
            defaults={"quantity": 1 if unit == "UNIT" else 10, "unit_price": price, "notes": "Valor teste"},
        )


def _populate_meat_test_data(organization):
    entries = [
        ("Cabeca", Decimal("12.00"), 1, 265, Decimal("165.000"), Decimal("622.00"), Decimal("538.00"), Decimal("602.00"), Decimal("87.000")),
        ("File", Decimal("22.00"), 2, 265, Decimal("174.000"), Decimal("657.00"), Decimal("625.00"), Decimal("716.00"), Decimal("21.000")),
        ("Limpeza", Decimal("18.00"), 3, 265, Decimal("142.500"), Decimal("538.00"), Decimal("612.00"), Decimal("579.00"), Decimal("8.500")),
        ("Pano", Decimal("18.00"), 4, 265, Decimal("85.000"), Decimal("321.00"), Decimal("242.00"), Decimal("319.00"), Decimal("2.500")),
        ("Rins", Decimal("4.00"), 1, 265, Decimal("10.000"), Decimal("37.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.000")),
        ("Ubere", Decimal("2.00"), 2, 265, Decimal("15.000"), Decimal("57.00"), Decimal("1216.00"), Decimal("416.00"), Decimal("0.000")),
    ]
    for name, price, week, slaughter, weight, average, general, previous, donation in entries:
        category, _ = MeatCategory.objects.get_or_create(
            organization=organization,
            name=name,
            defaults={"price_per_kg": price, "previous_price_per_kg": price, "donation_enabled": True, "is_active": True},
        )
        MeatProductionEntry.objects.get_or_create(
            organization=organization,
            category=category,
            reference_year=2026,
            reference_month=4,
            week_number=week,
            defaults={
                "slaughter_quantity": slaughter,
                "weight_kg": weight,
                "average_per_head_grams": average,
                "average_general_grams": general,
                "average_previous_month_grams": previous,
                "donation_kg": donation,
                "price_per_kg": price,
                "notes": "Lançamento teste",
            },
        )


def _populate_residue_test_data(organization):
    entries = [
        ("Sebo", "KG", Decimal("24680.00"), Decimal("0.70"), date(2026, 4, 2), Decimal("5400.00")),
        ("Bilis", "LITER", Decimal("520.00"), Decimal("55.90"), date(2026, 4, 4), Decimal("150.00")),
        ("Vergalho", "UNIT", Decimal("443.00"), Decimal("3.75"), date(2026, 4, 8), Decimal("210.00")),
        ("Livro", "UNIT", Decimal("370.00"), Decimal("4.52"), date(2026, 4, 9), Decimal("180.00")),
    ]
    for name, unit, target, price, collected_on, quantity in entries:
        category, _ = ResidueCategory.objects.get_or_create(
            organization=organization,
            name=name,
            defaults={"unit": unit, "target_amount": target, "unit_price": price, "is_active": True},
        )
        ResidueCollection.objects.get_or_create(
            organization=organization,
            category=category,
            collected_on=collected_on,
            defaults={"quantity": quantity, "notes": "Coleta teste"},
        )


def _populate_indemnity_test_data(organization):
    lookup_seed = {
        IndemnityLookupValue.FieldTypes.PRODUCT: ["Pernil", "Tripa", "File", "Bucho", "Cabeca", "Mocoto", "Pano", "Linguica", "Costela", "Retalho"],
        IndemnityLookupValue.FieldTypes.OWNER: ["Palmerina", "Jailson", "Luciene", "Marcio", "Equipe A", "Equipe B", "Vera", "Tonho", "F. H. Ivan", "Interno"],
        IndemnityLookupValue.FieldTypes.RESPONSIBLE: ["Tonho", "Vera", "Qualidade", "Expedicao", "Financeiro", "Operacao", "Marcio", "Carlos", "Juliana", "Interno"],
        IndemnityLookupValue.FieldTypes.REASON: ["Quebra operacional", "Desconto interno", "Venda parcial", "Acerto comercial", "Perda sanitaria", "Falha de processo", "Descarte", "Reaproveitamento", "Compensacao", "Erro de corte"],
    }
    for field_type, values in lookup_seed.items():
        for value in values[:10]:
            IndemnityLookupValue.objects.get_or_create(
                organization=organization,
                field_type=field_type,
                value=value,
                defaults={"is_active": True},
            )

    records = [
        (date(2026, 4, 1), "Pernil", "3 kg", Decimal("150.00"), Decimal("0.00"), "Palmerina", "Tonho", "Quebra operacional"),
        (date(2026, 4, 2), "Tripa", "2 kg", Decimal("80.00"), Decimal("50.00"), "Jailson", "Qualidade", "Venda parcial"),
        (date(2026, 4, 3), "File", "1,5 kg", Decimal("120.00"), Decimal("120.00"), "Luciene", "Financeiro", "Desconto interno"),
        (date(2026, 4, 4), "Bucho", "4 kg", Decimal("95.00"), Decimal("35.00"), "Marcio", "Operacao", "Reaproveitamento"),
    ]
    for occurred_on, product, quantity, outgoing, reversal, owner_name, responsible_name, reason in records:
        record, _ = IndemnityRecord.objects.get_or_create(
            organization=organization,
            occurred_on=occurred_on,
            product=product,
            defaults={
                "quantity_description": quantity,
                "outgoing_amount": outgoing,
                "reversal_amount": reversal,
                "owner_name": owner_name,
                "responsible_name": responsible_name,
                "reason": reason,
                "notes": "Ocorrência teste",
            },
        )
        sync_indemnity_lookup_values(
            organization,
            product=record.product,
            owner_name=record.owner_name,
            responsible_name=record.responsible_name,
            reason=record.reason,
        )


def _clear_income_test_data(organization):
    WeeklyIncomeEntry.objects.filter(organization=organization, notes__icontains="teste").delete()
    IncomeItem.objects.filter(organization=organization, entries__isnull=True).delete()


def _clear_meat_test_data(organization):
    MeatProductionEntry.objects.filter(organization=organization, notes__icontains="teste").delete()
    MeatCategory.objects.filter(organization=organization, entries__isnull=True).delete()


def _clear_residue_test_data(organization):
    ResidueCollection.objects.filter(organization=organization, notes__icontains="teste").delete()
    ResidueCategory.objects.filter(organization=organization, collections__isnull=True).delete()


def _clear_indemnity_test_data(organization):
    IndemnityRecord.objects.filter(organization=organization, notes__icontains="teste").delete()
    IndemnityLookupValue.objects.filter(organization=organization).delete()


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


class AdminDataToolkitView(MasterGlobalRequiredMixin, TemplateView):
    template_name = "organizations/admin_data_toolkit.html"

    def post(self, request, *args, **kwargs):
        organization = _get_target_organization(request)
        if not organization:
            messages.error(request, "Nenhuma organização disponível para popular dados.")
            return redirect("organizations:list")

        action = request.POST.get("action")
        scope = request.POST.get("scope")
        actions = {
            "income": (_populate_income_test_data, _clear_income_test_data, "Fontes de renda"),
            "meat": (_populate_meat_test_data, _clear_meat_test_data, "Carnes"),
            "residue": (_populate_residue_test_data, _clear_residue_test_data, "Resíduos"),
            "indemnity": (_populate_indemnity_test_data, _clear_indemnity_test_data, "Indenizações"),
        }

        if scope == "all":
            for populate, clear, _label in actions.values():
                (populate if action == "populate" else clear)(organization)
            messages.success(
                request,
                "Dados de teste atualizados para todos os módulos da organização ativa."
                if action == "populate"
                else "Todos os dados de teste da organização ativa foram removidos.",
            )
            return redirect("organizations:test-data")

        if scope in actions:
            populate, clear, label = actions[scope]
            (populate if action == "populate" else clear)(organization)
            messages.success(
                request,
                f"{label} {'populados' if action == 'populate' else 'limpos'} com sucesso na organização ativa.",
            )
        return redirect("organizations:test-data")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = _get_target_organization(self.request)
        context["page_title"] = "Popular dados de teste"
        context["page_description"] = "Popular e limpar até 10 valores de teste por tela na organização ativa."
        context["target_organization"] = organization
        if organization:
            context["module_cards"] = [
                {
                    "key": "income",
                    "title": "Fontes de renda",
                    "description": "Itens-base e lançamentos semanais de exemplo.",
                    "count": WeeklyIncomeEntry.objects.filter(organization=organization).count(),
                },
                {
                    "key": "meat",
                    "title": "Carnes",
                    "description": "Categorias e produções semanais com rendimento.",
                    "count": MeatProductionEntry.objects.filter(organization=organization).count(),
                },
                {
                    "key": "residue",
                    "title": "Resíduos",
                    "description": "Categorias e coletas diárias de teste.",
                    "count": ResidueCollection.objects.filter(organization=organization).count(),
                },
                {
                    "key": "indemnity",
                    "title": "Indenizações",
                    "description": "Ocorrências, dropdowns base e reversões.",
                    "count": IndemnityRecord.objects.filter(organization=organization).count(),
                },
            ]
        else:
            context["module_cards"] = []
        return context
