from django.urls import path

from . import views

app_name = "horarios"

urlpatterns = [
    path("", views.index, name="index"),
    path("tablero/", views.tablero, name="tablero"),
    path("tablero/grupos/<int:grupo_id>/guardar/", views.guardar_grupo, name="guardar_grupo"),
]
