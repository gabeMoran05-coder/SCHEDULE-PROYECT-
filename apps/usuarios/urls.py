from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("perfil/", views.perfil, name="perfil"),
]
