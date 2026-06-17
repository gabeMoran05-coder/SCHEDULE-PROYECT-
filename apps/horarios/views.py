from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.escuela.models import CicloEscolar, Grupo

from .models import BloqueHorario, DiaSemana, FichaAsignacion, HorarioClase


@login_required
def index(request):
    horarios = HorarioClase.objects.select_related("grupo", "materia", "contrato__docente", "bloque")[:80]
    return render(request, "horarios/index.html", {"horarios": horarios})


@login_required
def tablero(request):
    ciclo = CicloEscolar.objects.filter(activo=True).select_related("institucion").first()
    grupos = Grupo.objects.filter(ciclo=ciclo).order_by("grado", "letra") if ciclo else []
    bloques = BloqueHorario.objects.filter(ciclo=ciclo) if ciclo else []
    fichas = FichaAsignacion.objects.select_related(
        "asignacion__contrato__docente",
        "asignacion__materia",
        "grupo",
    )
    if ciclo:
        fichas = fichas.filter(grupo__ciclo=ciclo)

    context = {
        "ciclo": ciclo,
        "grupos": grupos,
        "bloques": bloques,
        "dias": DiaSemana.choices,
        "fichas": fichas[:120],
    }
    return render(request, "horarios/tablero.html", context)
