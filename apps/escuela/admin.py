from django.contrib import admin

from .models import (
    Alumno,
    AsignacionDocenteMateria,
    CicloEscolar,
    ContratoDocente,
    Docente,
    Grupo,
    Inscripcion,
    Institucion,
    Materia,
    Periodo,
    Tutor,
)

admin.site.register(AsignacionDocenteMateria)
admin.site.register(Alumno)
admin.site.register(CicloEscolar)
admin.site.register(ContratoDocente)
admin.site.register(Docente)
admin.site.register(Grupo)
admin.site.register(Inscripcion)
admin.site.register(Institucion)
admin.site.register(Materia)
admin.site.register(Periodo)
admin.site.register(Tutor)
