from django.urls import path

from . import views

app_name = "horarios"

urlpatterns = [
    path("", views.index, name="index"),
    path("tablero/", views.tablero, name="tablero"),
]
