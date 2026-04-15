from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class OrganizationOwnedModel(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="organização",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True


class IncomeItem(OrganizationOwnedModel):
    class Units(models.TextChoices):
        UNIT = "UNIT", "Unidade"
        KG = "KG", "Quilo"
        LITER = "LITER", "Litro"
        SERVICE = "SERVICE", "Serviço"

    name = models.CharField("item", max_length=100)
    unit = models.CharField("unidade", max_length=20, choices=Units.choices, default=Units.UNIT)
    default_price = models.DecimalField("preço padrão", max_digits=10, decimal_places=2)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "item de fonte de renda"
        verbose_name_plural = "itens de fontes de renda"
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class WeeklyIncomeEntry(OrganizationOwnedModel):
    item = models.ForeignKey(IncomeItem, on_delete=models.PROTECT, related_name="entries")
    reference_year = models.PositiveIntegerField("ano")
    reference_month = models.PositiveIntegerField("mês", validators=[MinValueValidator(1), MaxValueValidator(12)])
    week_number = models.PositiveSmallIntegerField("semana", validators=[MinValueValidator(1), MaxValueValidator(5)])
    quantity = models.PositiveIntegerField("quantidade")
    unit_price = models.DecimalField("preço unitário", max_digits=10, decimal_places=2)
    notes = models.TextField("observações", blank=True)

    class Meta:
        verbose_name = "lançamento semanal de renda"
        verbose_name_plural = "lançamentos semanais de renda"
        ordering = ["-reference_year", "-reference_month", "week_number", "item__name"]

    @property
    def calculated_total(self):
        return (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))

    def __str__(self):
        return f"{self.item} - S{self.week_number}/{self.reference_month}/{self.reference_year}"


class MeatCategory(OrganizationOwnedModel):
    name = models.CharField("categoria", max_length=100)
    price_per_kg = models.DecimalField("preço por kg", max_digits=10, decimal_places=2)
    previous_price_per_kg = models.DecimalField("preço anterior", max_digits=10, decimal_places=2, default=Decimal("0"))
    donation_enabled = models.BooleanField("aceita doação", default=True)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "categoria de carne"
        verbose_name_plural = "categorias de carnes"
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class MeatProductionEntry(OrganizationOwnedModel):
    category = models.ForeignKey(MeatCategory, on_delete=models.PROTECT, related_name="entries")
    reference_year = models.PositiveIntegerField("ano")
    reference_month = models.PositiveIntegerField("mês", validators=[MinValueValidator(1), MaxValueValidator(12)])
    week_number = models.PositiveSmallIntegerField("semana", validators=[MinValueValidator(1), MaxValueValidator(5)])
    slaughter_quantity = models.PositiveIntegerField("quantidade abatida")
    weight_kg = models.DecimalField("peso kg", max_digits=10, decimal_places=3)
    average_per_head_grams = models.DecimalField("média por cabeça g", max_digits=10, decimal_places=2)
    average_general_grams = models.DecimalField("média geral g", max_digits=10, decimal_places=2, default=0)
    average_previous_month_grams = models.DecimalField("média do mês anterior g", max_digits=10, decimal_places=2, default=0)
    donation_kg = models.DecimalField("doação kg", max_digits=10, decimal_places=3, default=0)
    price_per_kg = models.DecimalField("preço por kg", max_digits=10, decimal_places=2)
    notes = models.TextField("observações", blank=True)

    class Meta:
        verbose_name = "produção de carne"
        verbose_name_plural = "produções de carnes"
        ordering = ["-reference_year", "-reference_month", "week_number", "category__name"]

    @property
    def revenue_amount(self):
        return (self.weight_kg or Decimal("0")) * (self.price_per_kg or Decimal("0"))

    @property
    def donation_value(self):
        return (self.donation_kg or Decimal("0")) * (self.price_per_kg or Decimal("0"))

    @property
    def previous_trend(self):
        if self.average_per_head_grams > self.average_previous_month_grams:
            return "up"
        if self.average_per_head_grams < self.average_previous_month_grams:
            return "down"
        return "stable"

    @property
    def general_trend(self):
        if self.average_per_head_grams > self.average_general_grams:
            return "up"
        if self.average_per_head_grams < self.average_general_grams:
            return "down"
        return "stable"

    def __str__(self):
        return f"{self.category} - S{self.week_number}/{self.reference_month}/{self.reference_year}"


class ResidueCategory(OrganizationOwnedModel):
    class Units(models.TextChoices):
        KG = "KG", "Quilo"
        UNIT = "UNIT", "Unidade"
        LITER = "LITER", "Litro"

    name = models.CharField("categoria", max_length=100)
    unit = models.CharField("unidade", max_length=20, choices=Units.choices)
    target_amount = models.DecimalField("meta mensal", max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField("valor unitário", max_digits=10, decimal_places=2)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "categoria de resíduo"
        verbose_name_plural = "categorias de resíduos"
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class ResidueCollection(OrganizationOwnedModel):
    category = models.ForeignKey(ResidueCategory, on_delete=models.PROTECT, related_name="collections")
    collected_on = models.DateField("data de coleta")
    quantity = models.DecimalField("quantidade", max_digits=10, decimal_places=2)
    notes = models.TextField("observações", blank=True)

    class Meta:
        verbose_name = "coleta de resíduo"
        verbose_name_plural = "coletas de resíduos"
        ordering = ["-collected_on", "category__name"]

    @property
    def revenue_amount(self):
        return (self.quantity or Decimal("0")) * (self.category.unit_price or Decimal("0"))

    def __str__(self):
        return f"{self.category} - {self.collected_on:%d/%m/%Y}"


class IndemnityRecord(OrganizationOwnedModel):
    occurred_on = models.DateField("ocorrência")
    product = models.CharField("produto", max_length=120)
    quantity_description = models.CharField("quantidade/peso", max_length=80, blank=True)
    outgoing_amount = models.DecimalField("valor de saída", max_digits=10, decimal_places=2, default=0)
    reversal_amount = models.DecimalField("reversão", max_digits=10, decimal_places=2, default=0)
    owner_name = models.CharField("dono", max_length=120)
    responsible_name = models.CharField("responsável", max_length=120, blank=True)
    reason = models.CharField("motivo", max_length=160)
    notes = models.TextField("observações", blank=True)

    class Meta:
        verbose_name = "indenização"
        verbose_name_plural = "indenizações"
        ordering = ["-occurred_on", "product"]

    @property
    def net_amount(self):
        return (self.outgoing_amount or Decimal("0")) - (self.reversal_amount or Decimal("0"))

    @property
    def recovery_percentage(self):
        if not self.outgoing_amount:
            return Decimal("0")
        return ((self.reversal_amount or Decimal("0")) / self.outgoing_amount) * Decimal("100")

    @property
    def financial_status(self):
        if self.net_amount == 0:
            return "Sem prejuizo liquido"
        if self.reversal_amount == 0:
            return "Prejuizo integral"
        return "Perda parcialmente recuperada"

    def __str__(self):
        return f"{self.product} - {self.occurred_on:%d/%m/%Y}"


class AuditLog(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField("ação", max_length=120)
    module = models.CharField("módulo", max_length=80)
    object_description = models.CharField("objeto", max_length=200)
    details = models.TextField("detalhes", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "log de auditoria"
        verbose_name_plural = "logs de auditoria"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.module} - {self.action}"
