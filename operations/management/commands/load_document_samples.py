from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from operations.models import (
    IncomeItem,
    IndemnityRecord,
    MeatCategory,
    MeatProductionEntry,
    ResidueCategory,
    ResidueCollection,
    WeeklyIncomeEntry,
)
from organizations.models import Organization


class Command(BaseCommand):
    help = "Carrega dados de exemplo transcritos dos documentos operacionais enviados pelo usuario."

    def handle(self, *args, **options):
        organization = (
            Organization.objects.filter(slug="organizacao-demo").first()
            or Organization.objects.order_by("id").first()
        )
        if not organization:
            organization = Organization.objects.create(
                name="Organizacao Demo",
                slug="organizacao-demo",
                legal_name="AbatGus Operacao Demo",
                contact_email="demo@abatgus.local",
            )

        self.load_income_balance(organization)
        self.load_meat_report(organization)
        self.load_indemnities(organization)
        self.load_residues(organization)

        self.stdout.write(self.style.SUCCESS("Dados documentais carregados com sucesso."))

    def load_income_balance(self, organization):
        income_rows = [
            {"name": "Boi", "unit": "UNIT", "months": {2: {1: "150000.00"}, 3: {1: "47026.00", 2: "43266.00", 3: "45626.00", 4: "36068.00"}}},
            {"name": "Porco", "unit": "UNIT", "months": {2: {1: "50000.00"}, 3: {1: "14920.00", 2: "14240.00", 3: "13320.00", 4: "11020.00"}}},
            {"name": "Carnes", "unit": "KG", "months": {2: {1: "35000.00"}, 3: {1: "7670.94", 2: "7678.98", 3: "10316.55", 4: "7243.88"}}},
            {"name": "Sebo", "unit": "LITER", "months": {2: {1: "18000.00"}, 3: {3: "8414.00", 4: "3696.00"}}},
            {"name": "Livro", "unit": "KG", "months": {2: {1: "9000.00"}, 3: {3: "2280.00"}}},
            {"name": "Vergalho", "unit": "UNIT", "months": {2: {1: "7000.00"}, 3: {3: "1458.00"}}},
            {"name": "Bile", "unit": "LITER", "months": {2: {1: "3000.00"}, 3: {3: "300.00"}}},
            {"name": "Pedras", "unit": "UNIT", "months": {2: {1: "500.00"}, 3: {4: "50000.00"}}},
            {"name": "Frete Sao Joao", "unit": "SERVICE", "months": {2: {1: "1000.00"}, 3: {1: "300.00", 2: "350.00", 3: "350.00"}}},
            {"name": "Frete Palmerina", "unit": "SERVICE", "months": {2: {1: "1500.00"}, 3: {1: "450.00", 2: "520.00", 3: "520.00"}}},
            {"name": "Frete Correntes", "unit": "SERVICE", "months": {2: {1: "2000.00"}, 3: {1: "500.00", 2: "580.00", 3: "580.00", 4: "580.00"}}},
        ]

        item_names = [row["name"] for row in income_rows]
        WeeklyIncomeEntry.objects.filter(
            organization=organization,
            reference_year=2026,
            reference_month__in=[2, 3],
            item__name__in=item_names,
        ).delete()

        for row in income_rows:
            item, _ = IncomeItem.objects.update_or_create(
                organization=organization,
                name=row["name"],
                defaults={
                    "unit": row["unit"],
                    "default_price": Decimal(next(iter(next(iter(row["months"].values())).values()))),
                    "is_active": True,
                },
            )
            for month, weeks in row["months"].items():
                for week, amount in weeks.items():
                    WeeklyIncomeEntry.objects.create(
                        organization=organization,
                        item=item,
                        reference_year=2026,
                        reference_month=month,
                        week_number=week,
                        quantity=1,
                        unit_price=Decimal(amount),
                        notes="Carga manual do documento BALANCO GERAL FONTES DE RENDA (MARCO) e complemento de fevereiro para comparativo gerencial.",
                    )

    def load_meat_report(self, organization):
        meat_rows = {
            "Cabeca": {
                "category_defaults": {"price_per_kg": Decimal("12.00"), "previous_price_per_kg": Decimal("11.41")},
                "weeks": [
                    {"week": 1, "slaughter_quantity": 265, "weight_kg": "165.0", "average_per_head_grams": "622", "average_general_grams": "538", "average_previous_month_grams": "602", "revenue_amount": "1650.00", "donation_kg": "17.5"},
                    {"week": 2, "slaughter_quantity": 244, "weight_kg": "120.6", "average_per_head_grams": "492", "average_general_grams": "538", "average_previous_month_grams": "602", "revenue_amount": "1420.00", "donation_kg": "17.5"},
                    {"week": 3, "slaughter_quantity": 257, "weight_kg": "183.0", "average_per_head_grams": "712", "average_general_grams": "538", "average_previous_month_grams": "602", "revenue_amount": "2196.00", "donation_kg": "20.0"},
                    {"week": 4, "slaughter_quantity": 203, "weight_kg": "132.0", "average_per_head_grams": "650", "average_general_grams": "538", "average_previous_month_grams": "602", "revenue_amount": "1584.00", "donation_kg": "32.0"},
                ],
            },
            "File": {
                "category_defaults": {"price_per_kg": Decimal("22.00"), "previous_price_per_kg": Decimal("20.58")},
                "weeks": [
                    {"week": 1, "slaughter_quantity": 265, "weight_kg": "142.0", "average_per_head_grams": "535", "average_general_grams": "635", "average_previous_month_grams": "716", "revenue_amount": "2543.94", "donation_kg": "21.0"},
                    {"week": 2, "slaughter_quantity": 244, "weight_kg": "120.6", "average_per_head_grams": "492", "average_general_grams": "635", "average_previous_month_grams": "716", "revenue_amount": "2207.98", "donation_kg": "21.0"},
                    {"week": 3, "slaughter_quantity": 257, "weight_kg": "196.4", "average_per_head_grams": "764", "average_general_grams": "635", "average_previous_month_grams": "716", "revenue_amount": "4261.55", "donation_kg": "15.0"},
                    {"week": 4, "slaughter_quantity": 203, "weight_kg": "141.5", "average_per_head_grams": "697", "average_general_grams": "635", "average_previous_month_grams": "716", "revenue_amount": "3143.88", "donation_kg": "35.0"},
                ],
            },
            "Limpeza": {
                "category_defaults": {"price_per_kg": Decimal("18.00"), "previous_price_per_kg": Decimal("15.73")},
                "weeks": [
                    {"week": 1, "slaughter_quantity": 265, "weight_kg": "142.0", "average_per_head_grams": "535", "average_general_grams": "617", "average_previous_month_grams": "579", "revenue_amount": "2010.00", "donation_kg": "8.5"},
                    {"week": 2, "slaughter_quantity": 244, "weight_kg": "145.0", "average_per_head_grams": "594", "average_general_grams": "617", "average_previous_month_grams": "579", "revenue_amount": "2360.00", "donation_kg": "8.5"},
                    {"week": 3, "slaughter_quantity": 257, "weight_kg": "142.0", "average_per_head_grams": "552", "average_general_grams": "617", "average_previous_month_grams": "579", "revenue_amount": "2316.00", "donation_kg": "10.0"},
                    {"week": 4, "slaughter_quantity": 203, "weight_kg": "95.0", "average_per_head_grams": "467", "average_general_grams": "617", "average_previous_month_grams": "579", "revenue_amount": "1560.00", "donation_kg": "10.0"},
                ],
            },
            "Pano": {
                "category_defaults": {"price_per_kg": Decimal("18.00"), "previous_price_per_kg": Decimal("16.45")},
                "weeks": [
                    {"week": 1, "slaughter_quantity": 265, "weight_kg": "85.0", "average_per_head_grams": "320", "average_general_grams": "242", "average_previous_month_grams": "318", "revenue_amount": "1275.00", "donation_kg": "2.5"},
                    {"week": 2, "slaughter_quantity": 244, "weight_kg": "80.0", "average_per_head_grams": "327", "average_general_grams": "242", "average_previous_month_grams": "318", "revenue_amount": "1365.00", "donation_kg": "2.5"},
                    {"week": 3, "slaughter_quantity": 257, "weight_kg": "80.0", "average_per_head_grams": "314", "average_general_grams": "242", "average_previous_month_grams": "318", "revenue_amount": "1365.00", "donation_kg": "5.0"},
                    {"week": 4, "slaughter_quantity": 203, "weight_kg": "50.0", "average_per_head_grams": "246", "average_general_grams": "242", "average_previous_month_grams": "318", "revenue_amount": "850.00", "donation_kg": "0.0"},
                ],
            },
            "Rins": {
                "category_defaults": {"price_per_kg": Decimal("4.00"), "previous_price_per_kg": Decimal("4.00")},
                "weeks": [
                    {"week": 1, "slaughter_quantity": 265, "weight_kg": "10.0", "average_per_head_grams": "0", "average_general_grams": "0", "average_previous_month_grams": "0", "revenue_amount": "40.00", "donation_kg": "0.0"},
                    {"week": 2, "slaughter_quantity": 244, "weight_kg": "10.0", "average_per_head_grams": "0", "average_general_grams": "0", "average_previous_month_grams": "0", "revenue_amount": "40.00", "donation_kg": "0.0"},
                    {"week": 4, "slaughter_quantity": 203, "weight_kg": "10.0", "average_per_head_grams": "0", "average_general_grams": "0", "average_previous_month_grams": "0", "revenue_amount": "40.00", "donation_kg": "0.0"},
                ],
            },
            "Ubere": {
                "category_defaults": {"price_per_kg": Decimal("1.00"), "previous_price_per_kg": Decimal("1.00")},
                "weeks": [
                    {"week": 1, "slaughter_quantity": 125, "weight_kg": "152.0", "average_per_head_grams": "1210", "average_general_grams": "1210", "average_previous_month_grams": "1460", "revenue_amount": "152.00", "donation_kg": "0.0"},
                    {"week": 2, "slaughter_quantity": 123, "weight_kg": "196.0", "average_per_head_grams": "1590", "average_general_grams": "1210", "average_previous_month_grams": "1460", "revenue_amount": "196.00", "donation_kg": "0.0"},
                    {"week": 3, "slaughter_quantity": 121, "weight_kg": "178.0", "average_per_head_grams": "1470", "average_general_grams": "1210", "average_previous_month_grams": "1460", "revenue_amount": "178.00", "donation_kg": "0.0"},
                    {"week": 4, "slaughter_quantity": 109, "weight_kg": "156.0", "average_per_head_grams": "1430", "average_general_grams": "1210", "average_previous_month_grams": "1460", "revenue_amount": "156.00", "donation_kg": "0.0"},
                ],
            },
        }

        category_names = list(meat_rows.keys())
        MeatProductionEntry.objects.filter(
            organization=organization,
            reference_year=2026,
            reference_month=3,
            category__name__in=category_names,
        ).delete()

        for category_name, payload in meat_rows.items():
            category, _ = MeatCategory.objects.update_or_create(
                organization=organization,
                name=category_name,
                defaults={
                    **payload["category_defaults"],
                    "donation_enabled": True,
                    "is_active": True,
                },
            )
            for week_data in payload["weeks"]:
                weight = Decimal(week_data["weight_kg"])
                revenue = Decimal(week_data["revenue_amount"])
                price_per_kg = Decimal("0")
                if weight:
                    price_per_kg = (revenue / weight).quantize(Decimal("0.01"))

                MeatProductionEntry.objects.create(
                    organization=organization,
                    category=category,
                    reference_year=2026,
                    reference_month=3,
                    week_number=week_data["week"],
                    slaughter_quantity=week_data["slaughter_quantity"],
                    weight_kg=weight,
                    average_per_head_grams=Decimal(week_data["average_per_head_grams"]),
                    average_general_grams=Decimal(week_data["average_general_grams"]),
                    average_previous_month_grams=Decimal(week_data["average_previous_month_grams"]),
                    donation_kg=Decimal(week_data["donation_kg"]),
                    price_per_kg=price_per_kg,
                    notes="Carga manual do documento CARNES MARCO 2026.",
                )

    def load_indemnities(self, organization):
        IndemnityRecord.objects.filter(
            organization=organization,
            occurred_on__year=2026,
            occurred_on__month=3,
            product__in=["Bucho", "Mocotos", "Pernil", "Tripa", "Tripas/Jucema"],
        ).delete()

        rows = [
            {"occurred_on": "2026-03-01", "product": "Bucho", "quantity_description": "-", "outgoing_amount": "80.00", "reversal_amount": "0.00", "owner_name": "Palmerina", "responsible_name": "", "reason": "Falta de agua"},
            {"occurred_on": "2026-03-06", "product": "Mocotos", "quantity_description": "8 UND", "outgoing_amount": "20.00", "reversal_amount": "20.00", "owner_name": "Leleu", "responsible_name": "", "reason": "Desvio"},
            {"occurred_on": "2026-03-07", "product": "Pernil", "quantity_description": "30 kg", "outgoing_amount": "450.00", "reversal_amount": "180.00", "owner_name": "Jr de Iran", "responsible_name": "", "reason": "Quebra"},
            {"occurred_on": "2026-03-07", "product": "Pernil", "quantity_description": "9,1 kg", "outgoing_amount": "136.50", "reversal_amount": "0.00", "owner_name": "Lala", "responsible_name": "", "reason": "Quebra"},
            {"occurred_on": "2026-03-07", "product": "Pernil", "quantity_description": "7,5 kg", "outgoing_amount": "112.50", "reversal_amount": "0.00", "owner_name": "Jucelio", "responsible_name": "", "reason": "Quebra"},
            {"occurred_on": "2026-03-14", "product": "Pernil", "quantity_description": "14,1 kg", "outgoing_amount": "211.50", "reversal_amount": "163.50", "owner_name": "Vera", "responsible_name": "", "reason": "Quebra"},
            {"occurred_on": "2026-03-14", "product": "Tripa", "quantity_description": "3 kg", "outgoing_amount": "45.00", "reversal_amount": "45.00", "owner_name": "Tonho", "responsible_name": "", "reason": "Erro na entrega"},
            {"occurred_on": "2026-03-07", "product": "Tripas/Jucema", "quantity_description": "-", "outgoing_amount": "75.00", "reversal_amount": "75.00", "owner_name": "Jucieme", "responsible_name": "", "reason": "Desvio"},
        ]

        for row in rows:
            IndemnityRecord.objects.create(
                organization=organization,
                occurred_on=date.fromisoformat(row["occurred_on"]),
                product=row["product"],
                quantity_description=row["quantity_description"],
                outgoing_amount=Decimal(row["outgoing_amount"]),
                reversal_amount=Decimal(row["reversal_amount"]),
                owner_name=row["owner_name"],
                responsible_name=row["responsible_name"],
                reason=row["reason"],
                notes="Carga manual do documento INDENIZACOES MARCO DE 2026.",
            )

    def load_residues(self, organization):
        category_map = {
            "Sebo": {"unit": "KG", "target_amount": Decimal("24088"), "unit_price": Decimal("0.70")},
            "Bilis": {"unit": "LITER", "target_amount": Decimal("350"), "unit_price": Decimal("1.50")},
            "Vergalho": {"unit": "UNIT", "target_amount": Decimal("543"), "unit_price": Decimal("6.00")},
            "Livro": {"unit": "UNIT", "target_amount": Decimal("620"), "unit_price": Decimal("9.50")},
        }
        for name, defaults in category_map.items():
            ResidueCategory.objects.update_or_create(
                organization=organization,
                name=name,
                defaults={**defaults, "is_active": True},
            )

        ResidueCollection.objects.filter(
            organization=organization,
            category__name__in=category_map.keys(),
            collected_on__year=2026,
            collected_on__month__in=[2, 3],
        ).delete()

        rows = [
            ("2026-02-20", "Sebo", "10008"),
            ("2026-02-20", "Bilis", "200"),
            ("2026-02-20", "Vergalho", "50"),
            ("2026-02-20", "Livro", "370"),
            ("2026-02-23", "Sebo", "6000"),
            ("2026-02-23", "Vergalho", "290"),
            ("2026-03-03", "Bilis", "150"),
            ("2026-03-03", "Vergalho", "203"),
            ("2026-03-03", "Livro", "250"),
            ("2026-03-05", "Sebo", "8080"),
        ]
        for collected_on, category_name, quantity in rows:
            category = ResidueCategory.objects.get(organization=organization, name=category_name)
            ResidueCollection.objects.create(
                organization=organization,
                category=category,
                collected_on=date.fromisoformat(collected_on),
                quantity=Decimal(quantity),
                notes="Carga manual do documento RESIDUOS FEVEREIRO DE 2026.",
            )
