from django.urls import path

from . import views

app_name = "escuela"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("seleccionar-institucion/", views.seleccionar_institucion, name="seleccionar_institucion"),
    path("seleccionar-ciclo/", views.seleccionar_ciclo, name="seleccionar_ciclo"),
    path("alumnos/", views.alumnos, name="alumnos"),
    path("alumnos/agregar/", views.alumno_crear, name="alumno_crear"),
    path("alumnos/<int:alumno_id>/editar/", views.alumno_editar, name="alumno_editar"),
    path("alumnos/<int:alumno_id>/toggle-activo/", views.alumno_toggle_activo, name="alumno_toggle_activo"),
    path("alumnos/<int:alumno_id>/documentos/agregar/", views.alumno_documento_crear, name="alumno_documento_crear"),
    path("alumnos/<int:alumno_id>/", views.alumno_detalle, name="alumno_detalle"),
    path("docentes/", views.docentes, name="docentes"),
    path("docentes/agregar/", views.docente_crear, name="docente_crear"),
    path("docentes/<int:docente_id>/editar/", views.docente_editar, name="docente_editar"),
    path("docentes/<int:docente_id>/toggle-activo/", views.docente_toggle_activo, name="docente_toggle_activo"),
    path("docentes/<int:docente_id>/", views.docente_detalle, name="docente_detalle"),
    path("grupos/", views.grupos, name="grupos"),
    path("grupos/agregar/", views.grupo_crear, name="grupo_crear"),
    path("grupos/<int:grupo_id>/editar/", views.grupo_editar, name="grupo_editar"),
    path("grupos/<int:grupo_id>/toggle-activo/", views.grupo_toggle_activo, name="grupo_toggle_activo"),
    path("materias/", views.materias, name="materias"),
    path("materias/agregar/", views.materia_crear, name="materia_crear"),
    path("materias/<int:materia_id>/editar/", views.materia_editar, name="materia_editar"),
    path("materias/<int:materia_id>/toggle-activo/", views.materia_toggle_activo, name="materia_toggle_activo"),
    path("instituciones/agregar/", views.institucion_crear, name="institucion_crear"),
    path("ciclos/agregar/", views.ciclo_crear, name="ciclo_crear"),
]
