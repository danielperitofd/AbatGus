from django.urls import path

from .views import AdminDataToolkitView, OrganizationCreateView, OrganizationListView, OrganizationUpdateView


app_name = "organizations"

urlpatterns = [
    path("", OrganizationListView.as_view(), name="list"),
    path("dados-teste/", AdminDataToolkitView.as_view(), name="test-data"),
    path("novo/", OrganizationCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", OrganizationUpdateView.as_view(), name="update"),
]
