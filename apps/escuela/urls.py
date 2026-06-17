from django.urls import path

from . import views

app_name = "escuela"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("alumnos/", views.alumnos, name="alumnos"),
    path("alumnos/agregar/", views.alumno_crear, name="alumno_crear"),
    path("docentes/", views.docentes, name="docentes"),
    path("docentes/agregar/", views.docente_crear, name="docente_crear"),
    path("docentes/<int:docente_id>/", views.docente_detalle, name="docente_detalle"),
    path("grupos/", views.grupos, name="grupos"),
    path("grupos/agregar/", views.grupo_crear, name="grupo_crear"),
    path("materias/", views.materias, name="materias"),
    path("materias/agregar/", views.materia_crear, name="materia_crear"),
    path("instituciones/agregar/", views.institucion_crear, name="institucion_crear"),
]
