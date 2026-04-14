from django.db import models
from django.utils.text import slugify


class Organization(models.Model):
    name = models.CharField("nome", max_length=150)
    slug = models.SlugField("slug", max_length=160, unique=True, blank=True)
    legal_name = models.CharField("razão social", max_length=180, blank=True)
    document_number = models.CharField("documento", max_length=30, blank=True)
    contact_email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=30, blank=True)
    logo = models.ImageField("logo", upload_to="organizations/logos/", blank=True)
    primary_color = models.CharField("cor primária", max_length=7, default="#8A2E1E")
    secondary_color = models.CharField("cor secundária", max_length=7, default="#11212D")
    is_active = models.BooleanField("ativa", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "organização"
        verbose_name_plural = "organizações"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
