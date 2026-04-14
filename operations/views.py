from django.contrib import messages
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView, View

from core.mixins import OrganizationManagerRequiredMixin, OrganizationScopedMixin

from .forms import (
    IncomeItemForm,
    IndemnityRecordForm,
    MeatCategoryForm,
    MeatProductionEntryForm,
    ResidueCategoryForm,
    ResidueCollectionForm,
    SpreadsheetImportForm,
    WeeklyIncomeEntryForm,
)
from .models import (
    IncomeItem,
    IndemnityRecord,
    MeatCategory,
    MeatProductionEntry,
    ResidueCategory,
    ResidueCollection,
    WeeklyIncomeEntry,
)
from .services import (
    attach_income_status,
    attach_indemnity_status,
    attach_meat_status,
    attach_residue_status,
    import_income_rows,
    import_indemnity_rows,
    import_meat_rows,
    import_residue_rows,
    pdf_response,
    summarize_semaphores,
    workbook_response,
)


class OperationScopedQuerysetMixin(OrganizationScopedMixin, OrganizationManagerRequiredMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(*getattr(self, "select_related_fields", []))


class OperationListView(OperationScopedQuerysetMixin, ListView):
    status_attach = None
    module_title = ""
    module_description = ""
    create_url_name = ""
    import_url_name = ""
    export_excel_url_name = ""
    export_pdf_url_name = ""
    detail_url_name = ""
    supports_filters = True

    def get_queryset(self):
        queryset_base = super().get_queryset()
        queryset_base = self.apply_filters(queryset_base)
        queryset = list(queryset_base)
        status_attach = type(self).status_attach
        if status_attach:
            queryset = status_attach(queryset, queryset_base) if status_attach == attach_residue_status else status_attach(queryset)
        status = self.request.GET.get("status", "").strip()
        if status:
            queryset = [entry for entry in queryset if getattr(entry, "semaphore", {}).get("color") == status]
        return queryset

    def apply_filters(self, queryset):
        query = self.request.GET.get("q", "").strip()
        year = self.request.GET.get("year", "").strip()
        month = self.request.GET.get("month", "").strip()
        week = self.request.GET.get("week", "").strip()

        if year and hasattr(self.model, "reference_year"):
            queryset = queryset.filter(reference_year=year)
        if month and hasattr(self.model, "reference_month"):
            queryset = queryset.filter(reference_month=month)
        if week and hasattr(self.model, "week_number"):
            queryset = queryset.filter(week_number=week)
        if query:
            queryset = self.filter_by_query(queryset, query)
        return queryset

    def filter_by_query(self, queryset, query):
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.module_title,
                "description": self.module_description,
                "create_url_name": self.create_url_name,
                "import_url_name": self.import_url_name,
                "export_excel_url_name": self.export_excel_url_name,
                "export_pdf_url_name": self.export_pdf_url_name,
                "detail_url_name": self.detail_url_name,
                "status_summary": summarize_semaphores(context[self.context_object_name]),
                "filters": {
                    "q": self.request.GET.get("q", ""),
                    "year": self.request.GET.get("year", ""),
                    "month": self.request.GET.get("month", ""),
                    "week": self.request.GET.get("week", ""),
                    "status": self.request.GET.get("status", ""),
                },
                "supports_filters": self.supports_filters,
            }
        )
        return context


class CatalogListView(OperationScopedQuerysetMixin, ListView):
    template_name = "operations/catalog_list.html"
    context_object_name = "entries"
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""
    module_title = ""
    module_description = ""

    def filter_by_query(self, queryset, query):
        return queryset.filter(name__icontains=query)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.filter_by_query(queryset, query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.module_title,
                "description": self.module_description,
                "create_url_name": self.create_url_name,
                "update_url_name": self.update_url_name,
                "delete_url_name": self.delete_url_name,
                "filters": {"q": self.request.GET.get("q", "")},
            }
        )
        return context


class CatalogCreateView(OrganizationScopedMixin, OrganizationManagerRequiredMixin, CreateView):
    template_name = "shared/form_page.html"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["page_description"] = self.page_description
        return context


class OperationDetailView(OperationScopedQuerysetMixin, DetailView):
    template_name = "operations/entry_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.is_master_global:
            return obj
        if obj.organization_id != self.get_organization().id:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_fields"] = [
            (field.verbose_name, getattr(self.object, field.name))
            for field in self.object._meta.fields
        ]
        return context


class OperationUpdateView(OperationScopedQuerysetMixin, UpdateView):
    template_name = "shared/form_page.html"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)


class OperationDeleteView(OperationScopedQuerysetMixin, DeleteView):
    template_name = "shared/delete_confirm.html"

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, "Registro excluído com sucesso.")
            return response
        except ProtectedError:
            messages.error(
                request,
                "Não foi possível excluir porque existem dependências vinculadas a este registro.",
            )
            return redirect(self.get_success_url())


class CatalogUpdateView(OperationUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["page_description"] = self.page_description
        return context


class CatalogDeleteView(OperationDeleteView):
    pass


class SpreadsheetImportView(OrganizationManagerRequiredMixin, FormView):
    template_name = "operations/import_page.html"
    form_class = SpreadsheetImportForm
    importer = None
    success_url_name = ""
    page_title = ""
    page_description = ""
    sample_columns = ""

    def get_organization(self):
        org = getattr(self.request, "current_organization", None)
        if not org:
            raise Http404("Nenhuma organização ativa.")
        return org

    def form_valid(self, form):
        result = self.importer(self.get_organization(), form.cleaned_data["file"])
        if result.created_count:
            messages.success(self.request, f"{result.created_count} registros importados com sucesso.")
        if result.errors:
            for error in result.errors[:5]:
                messages.warning(self.request, error)
            if len(result.errors) > 5:
                messages.warning(self.request, f"{len(result.errors) - 5} erros adicionais foram ocultados.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["page_description"] = self.page_description
        context["sample_columns"] = self.sample_columns
        return context


class BaseExportView(OperationScopedQuerysetMixin, View):
    filename = "export"
    title = "Exportação"
    headers = []

    def get_queryset(self):
        queryset = self.model.objects.all()
        if getattr(self, "select_related_fields", None):
            queryset = queryset.select_related(*self.select_related_fields)
        if self.request.user.is_master_global:
            return queryset
        return queryset.filter(organization=self.get_organization())

    def get_rows(self, queryset):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        rows = self.get_rows(queryset)
        return self.render_export(rows)


class ExcelExportView(BaseExportView):
    def render_export(self, rows):
        return workbook_response(self.filename, self.title, self.headers, rows)


class PdfExportView(BaseExportView):
    def render_export(self, rows):
        return pdf_response(self.filename, self.title, self.headers, rows)


class WeeklyIncomeEntryListView(OperationListView):
    model = WeeklyIncomeEntry
    template_name = "operations/weekly_income_list.html"
    context_object_name = "entries"
    select_related_fields = ["item"]
    status_attach = attach_income_status
    module_title = "Fontes de renda"
    module_description = "Lançamentos semanais com cálculo por quantidade e valor unitário."
    create_url_name = "operations:income-create"
    import_url_name = "operations:income-import"
    export_excel_url_name = "operations:income-export-excel"
    export_pdf_url_name = "operations:income-export-pdf"
    detail_url_name = "operations:income-detail"

    def filter_by_query(self, queryset, query):
        return queryset.filter(item__name__icontains=query)


class WeeklyIncomeEntryCreateView(OrganizationScopedMixin, OrganizationManagerRequiredMixin, CreateView):
    model = WeeklyIncomeEntry
    form_class = WeeklyIncomeEntryForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("operations:income-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["item"].queryset = self.get_catalog_queryset(form.fields["item"].queryset)
        return form

    def form_valid(self, form):
        if not form.instance.organization_id and form.cleaned_data.get("item"):
            form.instance.organization = form.cleaned_data["item"].organization
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nova fonte de renda"
        context["page_description"] = "Lance a semana e deixe o sistema calcular o total."
        return context


class WeeklyIncomeEntryDetailView(OperationDetailView):
    model = WeeklyIncomeEntry
    select_related_fields = ["item"]


class WeeklyIncomeEntryUpdateView(OperationUpdateView):
    model = WeeklyIncomeEntry
    form_class = WeeklyIncomeEntryForm
    success_url_name = "operations:income-list"
    select_related_fields = ["item"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["item"].queryset = self.get_catalog_queryset(form.fields["item"].queryset)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar fonte de renda"
        context["page_description"] = "Atualize quantidade, preço ou observações do lançamento."
        return context


class WeeklyIncomeEntryDeleteView(OperationDeleteView):
    model = WeeklyIncomeEntry
    success_url_name = "operations:income-list"
    select_related_fields = ["item"]


class WeeklyIncomeImportView(SpreadsheetImportView):
    importer = staticmethod(import_income_rows)
    success_url_name = "operations:income-list"
    page_title = "Importar fontes de renda"
    page_description = "Importe planilhas XLSX ou CSV para lançamentos semanais."
    sample_columns = "item, ano, mes, semana, quantidade, preco_unitario, observacoes"


class WeeklyIncomeExcelExportView(ExcelExportView):
    model = WeeklyIncomeEntry
    select_related_fields = ["item"]
    filename = "fontes-renda"
    title = "Fontes de renda"
    headers = ["Item", "Ano", "Mês", "Semana", "Quantidade", "Preço unitário", "Total", "Observações"]

    def get_rows(self, queryset):
        return [
            [entry.item.name, entry.reference_year, entry.reference_month, entry.week_number, int(entry.quantity), float(entry.unit_price), float(entry.calculated_total), entry.notes]
            for entry in queryset
        ]


class WeeklyIncomePdfExportView(PdfExportView, WeeklyIncomeExcelExportView):
    pass


class MeatProductionEntryListView(OperationListView):
    model = MeatProductionEntry
    template_name = "operations/meat_list.html"
    context_object_name = "entries"
    select_related_fields = ["category"]
    status_attach = attach_meat_status
    module_title = "Carnes e partes do bovino"
    module_description = "Rendimento, peso, preço e doação por semana."
    create_url_name = "operations:meat-create"
    import_url_name = "operations:meat-import"
    export_excel_url_name = "operations:meat-export-excel"
    export_pdf_url_name = "operations:meat-export-pdf"
    detail_url_name = "operations:meat-detail"

    def filter_by_query(self, queryset, query):
        return queryset.filter(category__name__icontains=query)


class MeatProductionEntryCreateView(OrganizationScopedMixin, OrganizationManagerRequiredMixin, CreateView):
    model = MeatProductionEntry
    form_class = MeatProductionEntryForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("operations:meat-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = self.get_catalog_queryset(form.fields["category"].queryset)
        return form

    def form_valid(self, form):
        if not form.instance.organization_id and form.cleaned_data.get("category"):
            form.instance.organization = form.cleaned_data["category"].organization
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nova produção de carne"
        context["page_description"] = "Controle semanal de peso, rendimento, preço e doação."
        return context


class MeatProductionEntryDetailView(OperationDetailView):
    model = MeatProductionEntry
    select_related_fields = ["category"]


class MeatProductionEntryUpdateView(OperationUpdateView):
    model = MeatProductionEntry
    form_class = MeatProductionEntryForm
    success_url_name = "operations:meat-list"
    select_related_fields = ["category"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = self.get_catalog_queryset(form.fields["category"].queryset)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar produção de carne"
        context["page_description"] = "Ajuste rendimento, preço, média e doação."
        return context


class MeatProductionEntryDeleteView(OperationDeleteView):
    model = MeatProductionEntry
    success_url_name = "operations:meat-list"
    select_related_fields = ["category"]


class MeatImportView(SpreadsheetImportView):
    importer = staticmethod(import_meat_rows)
    success_url_name = "operations:meat-list"
    page_title = "Importar carnes"
    page_description = "Importe planilhas XLSX ou CSV de produção semanal."
    sample_columns = "categoria, ano, mes, semana, quantidade_abatida, peso_kg, media_cabeca_g, media_geral_g, media_mes_anterior_g, doacao_kg, preco_kg, observacoes"


class MeatExcelExportView(ExcelExportView):
    model = MeatProductionEntry
    select_related_fields = ["category"]
    filename = "carnes"
    title = "Carnes"
    headers = ["Categoria", "Ano", "Mês", "Semana", "Abate", "Peso kg", "Média por cabeça", "Média geral", "Mês anterior", "Doação kg", "Preço kg", "Receita", "Observações"]

    def get_rows(self, queryset):
        return [
            [
                entry.category.name,
                entry.reference_year,
                entry.reference_month,
                entry.week_number,
                entry.slaughter_quantity,
                float(entry.weight_kg),
                float(entry.average_per_head_grams),
                float(entry.average_general_grams),
                float(entry.average_previous_month_grams),
                float(entry.donation_kg),
                float(entry.price_per_kg),
                float(entry.revenue_amount),
                entry.notes,
            ]
            for entry in queryset
        ]


class MeatPdfExportView(PdfExportView, MeatExcelExportView):
    pass


class ResidueCollectionListView(OperationListView):
    model = ResidueCollection
    template_name = "operations/residue_list.html"
    context_object_name = "entries"
    select_related_fields = ["category"]
    status_attach = attach_residue_status
    module_title = "Resíduos e subprodutos"
    module_description = "Coleta diária com meta, perda e valor gerado."
    create_url_name = "operations:residue-create"
    import_url_name = "operations:residue-import"
    export_excel_url_name = "operations:residue-export-excel"
    export_pdf_url_name = "operations:residue-export-pdf"
    detail_url_name = "operations:residue-detail"

    def apply_filters(self, queryset):
        queryset = super().apply_filters(queryset)
        month = self.request.GET.get("month", "").strip()
        year = self.request.GET.get("year", "").strip()
        if year:
            queryset = queryset.filter(collected_on__year=year)
        if month:
            queryset = queryset.filter(collected_on__month=month)
        return queryset

    def filter_by_query(self, queryset, query):
        return queryset.filter(category__name__icontains=query)


class ResidueCollectionCreateView(OrganizationScopedMixin, OrganizationManagerRequiredMixin, CreateView):
    model = ResidueCollection
    form_class = ResidueCollectionForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("operations:residue-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = self.get_catalog_queryset(form.fields["category"].queryset)
        return form

    def form_valid(self, form):
        if not form.instance.organization_id and form.cleaned_data.get("category"):
            form.instance.organization = form.cleaned_data["category"].organization
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nova coleta de resíduo"
        context["page_description"] = "Cadastre coletas com metas, perdas e receita automática."
        return context


class ResidueCollectionDetailView(OperationDetailView):
    model = ResidueCollection
    select_related_fields = ["category"]


class ResidueCollectionUpdateView(OperationUpdateView):
    model = ResidueCollection
    form_class = ResidueCollectionForm
    success_url_name = "operations:residue-list"
    select_related_fields = ["category"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = self.get_catalog_queryset(form.fields["category"].queryset)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar coleta de resíduo"
        context["page_description"] = "Ajuste quantidade, data e observações sanitárias."
        return context


class ResidueCollectionDeleteView(OperationDeleteView):
    model = ResidueCollection
    success_url_name = "operations:residue-list"
    select_related_fields = ["category"]


class ResidueImportView(SpreadsheetImportView):
    importer = staticmethod(import_residue_rows)
    success_url_name = "operations:residue-list"
    page_title = "Importar resíduos"
    page_description = "Importe planilhas XLSX ou CSV com coletas diárias."
    sample_columns = "categoria, data, quantidade, unidade, valor_unitario, observacoes"


class ResidueExcelExportView(ExcelExportView):
    model = ResidueCollection
    select_related_fields = ["category"]
    filename = "residuos"
    title = "Resíduos"
    headers = ["Categoria", "Data", "Quantidade", "Valor unitário", "Receita", "Observações"]

    def get_rows(self, queryset):
        return [
            [entry.category.name, entry.collected_on.strftime("%d/%m/%Y"), float(entry.quantity), float(entry.category.unit_price), float(entry.revenue_amount), entry.notes]
            for entry in queryset
        ]


class ResiduePdfExportView(PdfExportView, ResidueExcelExportView):
    pass


class IndemnityRecordListView(OperationListView):
    model = IndemnityRecord
    template_name = "operations/indemnity_list.html"
    context_object_name = "entries"
    status_attach = attach_indemnity_status
    module_title = "Indenizações"
    module_description = "Ocorrências, reversões, dono e motivo da falha."
    create_url_name = "operations:indemnity-create"
    import_url_name = "operations:indemnity-import"
    export_excel_url_name = "operations:indemnity-export-excel"
    export_pdf_url_name = "operations:indemnity-export-pdf"
    detail_url_name = "operations:indemnity-detail"

    def apply_filters(self, queryset):
        queryset = super().apply_filters(queryset)
        month = self.request.GET.get("month", "").strip()
        year = self.request.GET.get("year", "").strip()
        if year:
            queryset = queryset.filter(occurred_on__year=year)
        if month:
            queryset = queryset.filter(occurred_on__month=month)
        return queryset

    def filter_by_query(self, queryset, query):
        return queryset.filter(product__icontains=query)


class IndemnityRecordCreateView(OrganizationScopedMixin, OrganizationManagerRequiredMixin, CreateView):
    model = IndemnityRecord
    form_class = IndemnityRecordForm
    template_name = "shared/form_page.html"
    success_url = reverse_lazy("operations:indemnity-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nova indenização"
        context["page_description"] = "Registre ocorrências, reversões e observações operacionais."
        return context


class IndemnityRecordDetailView(OperationDetailView):
    model = IndemnityRecord


class IndemnityRecordUpdateView(OperationUpdateView):
    model = IndemnityRecord
    form_class = IndemnityRecordForm
    success_url_name = "operations:indemnity-list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar indenização"
        context["page_description"] = "Ajuste ocorrência, valores e motivo operacional."
        return context


class IndemnityRecordDeleteView(OperationDeleteView):
    model = IndemnityRecord
    success_url_name = "operations:indemnity-list"


class IndemnityImportView(SpreadsheetImportView):
    importer = staticmethod(import_indemnity_rows)
    success_url_name = "operations:indemnity-list"
    page_title = "Importar indenizações"
    page_description = "Importe planilhas XLSX ou CSV de ocorrências e reversões."
    sample_columns = "data, produto, quantidade_peso, saida, reversao, dono, responsavel, motivo, observacoes"


class IndemnityExcelExportView(ExcelExportView):
    model = IndemnityRecord
    filename = "indenizacoes"
    title = "Indenizações"
    headers = ["Data", "Produto", "Quantidade/Peso", "Saída", "Reversão", "Líquido", "Dono", "Responsável", "Motivo", "Observações"]

    def get_rows(self, queryset):
        return [
            [entry.occurred_on.strftime("%d/%m/%Y"), entry.product, entry.quantity_description, float(entry.outgoing_amount), float(entry.reversal_amount), float(entry.net_amount), entry.owner_name, entry.responsible_name, entry.reason, entry.notes]
            for entry in queryset
        ]


class IndemnityPdfExportView(PdfExportView, IndemnityExcelExportView):
    pass


class IncomeItemListView(CatalogListView):
    model = IncomeItem
    module_title = "Itens de fontes de renda"
    module_description = "Cadastre os itens-base usados nos lançamentos semanais."
    create_url_name = "operations:income-item-create"
    update_url_name = "operations:income-item-update"
    delete_url_name = "operations:income-item-delete"


class IncomeItemCreateView(CatalogCreateView):
    model = IncomeItem
    form_class = IncomeItemForm
    success_url_name = "operations:income-item-list"
    page_title = "Novo item de fonte de renda"
    page_description = "Defina unidade e preço base para cálculo automático."


class IncomeItemUpdateView(CatalogUpdateView):
    model = IncomeItem
    form_class = IncomeItemForm
    success_url_name = "operations:income-item-list"
    page_title = "Editar item de fonte de renda"
    page_description = "Atualize preço padrão, unidade e status do item."


class IncomeItemDeleteView(CatalogDeleteView):
    model = IncomeItem
    success_url_name = "operations:income-item-list"


class MeatCategoryListView(CatalogListView):
    model = MeatCategory
    module_title = "Categorias de carnes"
    module_description = "Cadastre faixas de preço e parâmetros padrão por categoria."
    create_url_name = "operations:meat-category-create"
    update_url_name = "operations:meat-category-update"
    delete_url_name = "operations:meat-category-delete"


class MeatCategoryCreateView(CatalogCreateView):
    model = MeatCategory
    form_class = MeatCategoryForm
    success_url_name = "operations:meat-category-list"
    page_title = "Nova categoria de carne"
    page_description = "Configure o preço por kg, preço anterior e disponibilidade de doação."


class MeatCategoryUpdateView(CatalogUpdateView):
    model = MeatCategory
    form_class = MeatCategoryForm
    success_url_name = "operations:meat-category-list"
    page_title = "Editar categoria de carne"
    page_description = "Mantenha os parâmetros padrão usados nos lançamentos de carnes."


class MeatCategoryDeleteView(CatalogDeleteView):
    model = MeatCategory
    success_url_name = "operations:meat-category-list"


class ResidueCategoryListView(CatalogListView):
    model = ResidueCategory
    module_title = "Categorias de resíduos"
    module_description = "Cadastre metas mensais, unidade e valor unitário por subproduto."
    create_url_name = "operations:residue-category-create"
    update_url_name = "operations:residue-category-update"
    delete_url_name = "operations:residue-category-delete"


class ResidueCategoryCreateView(CatalogCreateView):
    model = ResidueCategory
    form_class = ResidueCategoryForm
    success_url_name = "operations:residue-category-list"
    page_title = "Nova categoria de resíduo"
    page_description = "Defina meta mensal e valor unitário para semáforo e receita."


class ResidueCategoryUpdateView(CatalogUpdateView):
    model = ResidueCategory
    form_class = ResidueCategoryForm
    success_url_name = "operations:residue-category-list"
    page_title = "Editar categoria de resíduo"
    page_description = "Atualize metas, unidade e valor base dos resíduos."


class ResidueCategoryDeleteView(CatalogDeleteView):
    model = ResidueCategory
    success_url_name = "operations:residue-category-list"
