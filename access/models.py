from django.conf import settings
from django.db import models


class Module(models.Model):
    name = models.CharField("nome", max_length=120)
    code = models.SlugField("código", unique=True)
    icon = models.CharField("ícone", max_length=60, blank=True)
    description = models.CharField("descrição", max_length=255, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="módulo pai",
    )
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "módulo"
        verbose_name_plural = "módulos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationModuleAccess(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="module_accesses",
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="organization_accesses")
    enabled = models.BooleanField("habilitado", default=True)

    class Meta:
        verbose_name = "acesso da organização"
        verbose_name_plural = "acessos das organizações"
        unique_together = ("organization", "module")

    def __str__(self):
        return f"{self.organization} - {self.module}"


class UserModuleAccess(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="module_accesses",
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="user_accesses")
    can_view = models.BooleanField("visualizar", default=True)
    can_add = models.BooleanField("criar", default=False)
    can_change = models.BooleanField("editar", default=False)
    can_delete = models.BooleanField("excluir", default=False)

    class Meta:
        verbose_name = "acesso do usuário"
        verbose_name_plural = "acessos dos usuários"
        unique_together = ("user", "module")

    def __str__(self):
        return f"{self.user} - {self.module}"
