from datetime import date
from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Avg

from .models import (
    IncomeItem,
    IndemnityRecord,
    MeatCategory,
    MeatProductionEntry,
    ResidueCategory,
    ResidueCollection,
    WeeklyIncomeEntry,
)


def parse_decimal_input(value):
    if isinstance(value, Decimal):
        return value
    normalized = str(value or "").replace("R$", "").strip()
    normalized = normalized.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized or "0")
    except (InvalidOperation, ValueError):
        return Decimal("0")


class PriceAwareSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        instance = getattr(value, "instance", None)
        if instance and hasattr(instance, "default_price"):
            option["attrs"]["data-default-price"] = str(instance.default_price)
        return option


class CategoryPriceSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        instance = getattr(value, "instance", None)
        if instance and hasattr(instance, "price_per_kg"):
            option["attrs"]["data-default-price"] = str(instance.price_per_kg)
        return option


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
                field.widget.attrs["role"] = "switch"
            else:
                field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class SpreadsheetImportForm(forms.Form):
    file = forms.FileField(label="Planilha")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["class"] = "form-control"


class IncomeItemForm(BootstrapModelForm):
    class Meta:
        model = IncomeItem
        fields = ["name", "unit", "default_price", "is_active"]


class MeatCategoryForm(BootstrapModelForm):
    price_per_kg = forms.CharField(label="Preço por Kg")
    previous_price_per_kg = forms.CharField(label="Preço Anterior")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price_per_kg"].widget = forms.TextInput(
            attrs={"class": "form-control", "inputmode": "decimal"}
        )
        self.fields["previous_price_per_kg"].widget = forms.TextInput(
            attrs={"class": "form-control", "inputmode": "decimal"}
        )
        if self.instance and self.instance.pk:
            self.initial["price_per_kg"] = f"R$ {self.instance.price_per_kg:.2f}".replace(".", ",")
            self.initial["previous_price_per_kg"] = f"R$ {self.instance.previous_price_per_kg:.2f}".replace(".", ",")

    class Meta:
        model = MeatCategory
        fields = ["name", "price_per_kg", "previous_price_per_kg", "donation_enabled", "is_active"]

    def clean_price_per_kg(self):
        value = str(self.cleaned_data["price_per_kg"]).replace("R$", "").strip()
        return value.replace(".", "").replace(",", ".")

    def clean_previous_price_per_kg(self):
        value = str(self.cleaned_data["previous_price_per_kg"]).replace("R$", "").strip()
        return value.replace(".", "").replace(",", ".")


class ResidueCategoryForm(BootstrapModelForm):
    class Meta:
        model = ResidueCategory
        fields = ["name", "unit", "target_amount", "unit_price", "is_active"]


class WeeklyIncomeEntryForm(BootstrapModelForm):
    unit_price = forms.CharField(label="Preço unitário")
    MONTH_CHOICES = [
        (1, "Janeiro"),
        (2, "Fevereiro"),
        (3, "Marco"),
        (4, "Abril"),
        (5, "Maio"),
        (6, "Junho"),
        (7, "Julho"),
        (8, "Agosto"),
        (9, "Setembro"),
        (10, "Outubro"),
        (11, "Novembro"),
        (12, "Dezembro"),
    ]
    WEEK_CHOICES = [
        (1, "Semana 1"),
        (2, "Semana 2"),
        (3, "Semana 3"),
        (4, "Semana 4"),
        (5, "Semana 5"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].widget = PriceAwareSelect(
            attrs={
                "class": "form-select",
                "data-autofill-target": "id_unit_price",
            }
        )
        self.fields["reference_month"].widget = forms.Select(
            choices=self.MONTH_CHOICES,
            attrs={"class": "form-select"},
        )
        self.fields["week_number"].widget = forms.Select(
            choices=self.WEEK_CHOICES,
            attrs={"class": "form-select"},
        )
        self.fields["reference_year"].initial = self.initial.get("reference_year") or date.today().year
        self.fields["reference_month"].initial = self.initial.get("reference_month") or date.today().month
        self.fields["quantity"].widget.attrs.update({"step": "1", "min": "0"})
        self.fields["unit_price"].widget = forms.TextInput(
            attrs={"class": "form-control", "inputmode": "decimal"}
        )

    class Meta:
        model = WeeklyIncomeEntry
        fields = ["item", "reference_year", "reference_month", "week_number", "quantity", "unit_price", "notes"]

    def clean_unit_price(self):
        value = str(self.cleaned_data["unit_price"]).replace("R$", "").strip()
        return value.replace(".", "").replace(",", ".")


class MeatProductionEntryForm(BootstrapModelForm):
    price_per_kg = forms.CharField(label="Preço por kg")
    MONTH_CHOICES = WeeklyIncomeEntryForm.MONTH_CHOICES
    WEEK_CHOICES = WeeklyIncomeEntryForm.WEEK_CHOICES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].label = "Categoria"
        self.fields["category"].widget = CategoryPriceSelect(
            attrs={
                "class": "form-select",
                "data-autofill-target": "id_price_per_kg",
            }
        )
        self.fields["reference_month"].widget = forms.Select(
            choices=self.MONTH_CHOICES,
            attrs={"class": "form-select"},
        )
        self.fields["week_number"].widget = forms.Select(
            choices=self.WEEK_CHOICES,
            attrs={"class": "form-select"},
        )
        self.fields["reference_year"].initial = self.initial.get("reference_year") or date.today().year
        self.fields["reference_month"].initial = self.initial.get("reference_month") or date.today().month
        self.fields["price_per_kg"].widget = forms.TextInput(
            attrs={"class": "form-control", "inputmode": "decimal"}
        )
        for field_name in [
            "slaughter_quantity",
            "weight_kg",
            "average_per_head_grams",
            "average_general_grams",
            "average_previous_month_grams",
            "donation_kg",
        ]:
            self.fields[field_name].widget.attrs["data-select-on-focus"] = "true"

    class Meta:
        model = MeatProductionEntry
        fields = [
            "category",
            "reference_year",
            "reference_month",
            "week_number",
            "slaughter_quantity",
            "weight_kg",
            "average_per_head_grams",
            "average_general_grams",
            "average_previous_month_grams",
            "donation_kg",
            "price_per_kg",
            "notes",
        ]

    def clean_price_per_kg(self):
        value = str(self.cleaned_data["price_per_kg"]).replace("R$", "").strip()
        return value.replace(".", "").replace(",", ".")

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        year = cleaned_data.get("reference_year")
        month = cleaned_data.get("reference_month")
        slaughter_quantity = cleaned_data.get("slaughter_quantity") or 0
        weight_kg = parse_decimal_input(cleaned_data.get("weight_kg"))

        if slaughter_quantity and weight_kg:
            cleaned_data["average_per_head_grams"] = (weight_kg / Decimal(slaughter_quantity)) * Decimal("1000")

        if category and year and month:
            previous_entry = (
                MeatProductionEntry.objects.filter(
                    organization=category.organization,
                    category=category,
                    reference_year=year if month > 1 else year - 1,
                    reference_month=month - 1 if month > 1 else 12,
                )
                .order_by("-week_number")
                .first()
            )
            previous_average = previous_entry.average_per_head_grams if previous_entry else Decimal("0")
            general_average = (
                MeatProductionEntry.objects.filter(
                    organization=category.organization,
                    category=category,
                    reference_year=year - 1,
                ).aggregate(avg=Avg("average_per_head_grams"))["avg"]
                or Decimal("0")
            )

            if not cleaned_data.get("average_previous_month_grams"):
                cleaned_data["average_previous_month_grams"] = previous_average
            if not cleaned_data.get("average_general_grams"):
                cleaned_data["average_general_grams"] = general_average

        return cleaned_data


class ResidueCollectionForm(BootstrapModelForm):
    class Meta:
        model = ResidueCollection
        fields = ["category", "collected_on", "quantity", "notes"]
        widgets = {"collected_on": forms.DateInput(attrs={"type": "date"})}


class IndemnityRecordForm(BootstrapModelForm):
    class Meta:
        model = IndemnityRecord
        fields = [
            "occurred_on",
            "product",
            "quantity_description",
            "outgoing_amount",
            "reversal_amount",
            "owner_name",
            "responsible_name",
            "reason",
            "notes",
        ]
        widgets = {"occurred_on": forms.DateInput(attrs={"type": "date"})}
