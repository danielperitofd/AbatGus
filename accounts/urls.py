from django.urls import path

from .views import AbatGusLoginView, AbatGusLogoutView, UserCreateView, UserListView, UserUpdateView


app_name = "accounts"

urlpatterns = [
    path("login/", AbatGusLoginView.as_view(), name="login"),
    path("logout/", AbatGusLogoutView.as_view(), name="logout"),
    path("usuarios/", UserListView.as_view(), name="list"),
    path("usuarios/novo/", UserCreateView.as_view(), name="create"),
    path("usuarios/<int:pk>/editar/", UserUpdateView.as_view(), name="update"),
]
