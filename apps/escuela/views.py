from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Alumno, CicloEscolar, ContratoDocente, Docente, Grupo, Institucion, Materia


@login_required
def dashboard(request):
    context = {
        "total_instituciones": Institucion.objects.count(),
        "ciclo_activo": CicloEscolar.objects.filter(activo=True).select_related("institucion").first(),
        "total_alumnos": Alumno.objects.filter(activo=True).count(),
        "total_docentes": Docente.objects.filter(activo=True).count(),
        "total_contratos": ContratoDocente.objects.filter(activo=True).count(),
        "total_grupos": Grupo.objects.count(),
        "total_materias": Materia.objects.count(),
    }
    return render(request, "escuela/dashboard.html", context)


@login_required
def alumnos(request):
    return render(request, "escuela/alumnos/index.html", {"alumnos": Alumno.objects.all()[:50]})


@login_required
def docentes(request):
    return render(request, "escuela/docentes/index.html", {"docentes": Docente.objects.all()[:50]})


@login_required
def grupos(request):
    return render(request, "escuela/grupos/index.html", {"grupos": Grupo.objects.all()[:50]})


@login_required
def materias(request):
    return render(request, "escuela/materias/index.html", {"materias": Materia.objects.all()[:50]})
