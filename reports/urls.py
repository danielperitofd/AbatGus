from django.urls import path

from .views import ReportsHubView


app_name = "reports"

urlpatterns = [
    path("", ReportsHubView.as_view(), name="hub"),
]
