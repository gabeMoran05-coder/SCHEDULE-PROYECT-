from django.contrib import admin

from .models import BloqueHorario, DisponibilidadDocente, FichaAsignacion, HorarioClase

admin.site.register(BloqueHorario)
admin.site.register(DisponibilidadDocente)
admin.site.register(FichaAsignacion)
admin.site.register(HorarioClase)
