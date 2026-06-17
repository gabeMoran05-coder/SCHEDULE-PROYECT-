from django.urls import path

from . import views

app_name = "escuela"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("alumnos/", views.alumnos, name="alumnos"),
    path("docentes/", views.docentes, name="docentes"),
    path("grupos/", views.grupos, name="grupos"),
    path("materias/", views.materias, name="materias"),
]
