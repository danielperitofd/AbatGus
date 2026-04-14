from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        MASTER = "MASTER", "Master Global"
        MANAGER = "MANAGER", "Gestor da Organização"
        ASSISTANT = "ASSISTANT", "Usuário Auxiliar"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="organização",
    )
    role = models.CharField("perfil", max_length=20, choices=Roles.choices, default=Roles.ASSISTANT)
    avatar = models.ImageField("foto", upload_to="users/avatars/", blank=True)
    phone = models.CharField("telefone", max_length=30, blank=True)
    job_title = models.CharField("cargo", max_length=100, blank=True)
    internal_notes = models.TextField("observações internas", blank=True)

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    @property
    def display_name(self):
        full_name = self.get_full_name().strip()
        return full_name or self.username

    @property
    def is_master_global(self):
        return self.role == self.Roles.MASTER or self.is_superuser

    @property
    def is_organization_manager(self):
        return self.role == self.Roles.MANAGER
