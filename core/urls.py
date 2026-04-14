from django.urls import path

from .views import DashboardView, SwitchOrganizationView


app_name = "core"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("trocar-organizacao/<int:pk>/", SwitchOrganizationView.as_view(), name="switch-organization"),
]
