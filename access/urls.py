from django.urls import path

from .views import AccessOverviewView


app_name = "access"

urlpatterns = [
    path("", AccessOverviewView.as_view(), name="overview"),
]
