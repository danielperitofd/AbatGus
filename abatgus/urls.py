from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("core.urls")),
    path("contas/", include("accounts.urls")),
    path("organizacoes/", include("organizations.urls")),
    path("acessos/", include("access.urls")),
    path("operacoes/", include("operations.urls")),
    path("relatorios/", include("reports.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
