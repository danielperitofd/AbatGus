from django.conf import settings
from django.core.management.base import BaseCommand

from access.models import Module
from accounts.models import User
from operations.models import IncomeItem, MeatCategory, ResidueCategory
from organizations.models import Organization


class Command(BaseCommand):
    help = "Cria dados iniciais do AbatGus, incluindo master global e catálogos padrão."

    def handle(self, *args, **options):
        organization, _ = Organization.objects.get_or_create(
            slug="organizacao-demo",
            defaults={
                "name": "Organização Demo",
                "legal_name": "AbatGus Operação Demo",
                "document_number": "00.000.000/0001-00",
                "contact_email": "demo@abatgus.local",
            },
        )

        master, created = User.objects.get_or_create(
            username=settings.ABATGUS_MASTER_USERNAME,
            defaults={
                "first_name": "Daniel",
                "last_name": "Gus",
                "email": "master@abatgus.local",
                "role": User.Roles.MASTER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        master.role = User.Roles.MASTER
        master.is_staff = True
        master.is_superuser = True
        master.set_password(settings.ABATGUS_MASTER_PASSWORD)
        master.save()

        manager, _ = User.objects.get_or_create(
            username="gestor.demo",
            defaults={
                "first_name": "Gestor",
                "last_name": "Demo",
                "organization": organization,
                "role": User.Roles.MANAGER,
                "email": "gestor@abatgus.local",
                "is_staff": True,
            },
        )
        manager.organization = organization
        manager.role = User.Roles.MANAGER
        manager.is_staff = True
        manager.set_password("Gestor@123")
        manager.save()

        modules = [
            ("dashboard", "Dashboard", "Visão geral da operação", "bi-grid"),
            ("fontes-renda", "Fontes de renda", "Lançamentos semanais de receita", "bi-cash-coin"),
            ("carnes", "Carnes", "Produção por categoria e semana", "bi-box-seam"),
            ("residuos", "Resíduos", "Controle sanitário e subprodutos", "bi-recycle"),
            ("indenizacoes", "Indenizações", "Ocorrências com impacto financeiro", "bi-exclamation-octagon"),
            ("relatorios", "Relatórios", "Exportações e análises", "bi-bar-chart"),
            ("configuracoes", "Configurações", "Usuários e acessos", "bi-sliders"),
            ("admin-tools", "Admin Tools", "Gestão global de organizações", "bi-diagram-3"),
        ]
        for code, name, description, icon in modules:
            Module.objects.get_or_create(
                code=code,
                defaults={"name": name, "description": description, "icon": icon},
            )

        for name, unit, price in [
            ("Boi", "UNIT", 180),
            ("Porco", "UNIT", 80),
            ("Carnes", "KG", 12),
            ("Sebo", "LITER", 0.70),
            ("Livro", "KG", 9.50),
            ("Vergalho", "UNIT", 6),
            ("Bile", "LITER", 1.50),
        ]:
            IncomeItem.objects.get_or_create(
                organization=organization,
                name=name,
                defaults={"unit": unit, "default_price": price},
            )

        for name, price, previous in [
            ("Cabeça", 12, 11.41),
            ("Filé", 22, 20.58),
            ("Limpeza", 18, 15.73),
            ("Pano", 18, 16.45),
            ("Rins", 10, 10),
            ("Úbere", 8, 8),
        ]:
            MeatCategory.objects.get_or_create(
                organization=organization,
                name=name,
                defaults={"price_per_kg": price, "previous_price_per_kg": previous},
            )

        for name, unit, target, price in [
            ("Sebo", "KG", 24088, 0.70),
            ("Livro", "UNIT", 350, 9.50),
            ("Vergalho", "UNIT", 620, 6),
            ("Bilis", "LITER", 543, 1.50),
        ]:
            ResidueCategory.objects.get_or_create(
                organization=organization,
                name=name,
                defaults={"unit": unit, "target_amount": target, "unit_price": price},
            )

        if created:
            self.stdout.write(self.style.SUCCESS("Master global criado com sucesso."))
        self.stdout.write(self.style.SUCCESS("Seed inicial concluída."))
