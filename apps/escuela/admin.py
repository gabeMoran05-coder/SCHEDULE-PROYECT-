from django.contrib import admin

from .models import (
    Alumno,
    AsignacionDocenteMateria,
    CicloEscolar,
    ContratoDocente,
    Docente,
    DocumentoAlumno,
    Grupo,
    Inscripcion,
    Institucion,
    KardexAlumno,
    Materia,
    Periodo,
    Tutor,
)

admin.site.register(AsignacionDocenteMateria)
admin.site.register(Alumno)
admin.site.register(CicloEscolar)
admin.site.register(ContratoDocente)
admin.site.register(Docente)
admin.site.register(DocumentoAlumno)
admin.site.register(Grupo)
admin.site.register(Inscripcion)
admin.site.register(Institucion)
admin.site.register(KardexAlumno)
admin.site.register(Materia)
admin.site.register(Periodo)
admin.site.register(Tutor)
