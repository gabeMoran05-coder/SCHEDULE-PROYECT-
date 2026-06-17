from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import AlumnoForm, DocenteForm, GrupoForm, InstitucionForm, MateriaForm
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
    alumnos_qs = Alumno.objects.select_related("institucion", "tutor")
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")

    if busqueda:
        alumnos_qs = alumnos_qs.filter(
            Q(matricula__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(tutor__nombre__icontains=busqueda)
        )
    if estado == "activo":
        alumnos_qs = alumnos_qs.filter(activo=True)
    elif estado == "inactivo":
        alumnos_qs = alumnos_qs.filter(activo=False)

    alumnos_qs = alumnos_qs[:80]
    return render(
        request,
        "escuela/alumnos/index.html",
        {"alumnos": alumnos_qs, "busqueda": busqueda, "estado": estado},
    )


@login_required
def alumno_crear(request):
    form = AlumnoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Alumno registrado correctamente.")
        return redirect("escuela:alumnos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar alumno", "volver_url": "escuela:alumnos"})


@login_required
def docentes(request):
    docentes_qs = Docente.objects.prefetch_related("contratos")
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")

    if busqueda:
        docentes_qs = docentes_qs.filter(
            Q(numero_empleado__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(correo__icontains=busqueda)
        )
    if estado == "activo":
        docentes_qs = docentes_qs.filter(activo=True)
    elif estado == "inactivo":
        docentes_qs = docentes_qs.filter(activo=False)

    docentes_qs = docentes_qs[:80]
    return render(
        request,
        "escuela/docentes/index.html",
        {"docentes": docentes_qs, "busqueda": busqueda, "estado": estado},
    )


@login_required
def docente_crear(request):
    form = DocenteForm(request.POST or None)
    ciclo_activo = CicloEscolar.objects.filter(activo=True).select_related("institucion").first()

    if request.method == "POST" and form.is_valid():
        docente = form.save()
        if ciclo_activo:
            ContratoDocente.objects.update_or_create(
                docente=docente,
                institucion=ciclo_activo.institucion,
                ciclo=ciclo_activo,
                defaults={
                    "horas_semanales": form.cleaned_data["horas_semanales"],
                    "es_tutor": form.cleaned_data["es_tutor"],
                    "activo": True,
                },
            )
        messages.success(request, "Docente registrado correctamente.")
        return redirect("escuela:docentes")

    return render(
        request,
        "escuela/formulario.html",
        {
            "form": form,
            "titulo": "Agregar docente",
            "volver_url": "escuela:docentes",
            "ayuda": "Las horas semanales se guardan en el ciclo activo.",
        },
    )


@login_required
def grupos(request):
    grupos_qs = Grupo.objects.select_related("ciclo", "ciclo__institucion")
    grado = request.GET.get("grado", "")
    turno = request.GET.get("turno", "")

    if grado:
        grupos_qs = grupos_qs.filter(grado=grado)
    if turno:
        grupos_qs = grupos_qs.filter(turno=turno)

    grupos_qs = grupos_qs[:80]
    return render(
        request,
        "escuela/grupos/index.html",
        {"grupos": grupos_qs, "grado": grado, "turno": turno},
    )


@login_required
def grupo_crear(request):
    form = GrupoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grupo registrado correctamente.")
        return redirect("escuela:grupos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar grupo", "volver_url": "escuela:grupos"})


@login_required
def materias(request):
    materias_qs = Materia.objects.all()
    busqueda = request.GET.get("q", "").strip()
    grado = request.GET.get("grado", "")

    if busqueda:
        materias_qs = materias_qs.filter(Q(clave__icontains=busqueda) | Q(nombre__icontains=busqueda))
    if grado:
        materias_qs = materias_qs.filter(grado=grado)

    materias_qs = materias_qs[:80]
    return render(
        request,
        "escuela/materias/index.html",
        {"materias": materias_qs, "busqueda": busqueda, "grado": grado},
    )


@login_required
def materia_crear(request):
    form = MateriaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Materia registrada correctamente.")
        return redirect("escuela:materias")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar materia", "volver_url": "escuela:materias"})


@login_required
def institucion_crear(request):
    form = InstitucionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Institucion registrada correctamente.")
        return redirect("escuela:dashboard")
    return render(
        request,
        "escuela/formulario.html",
        {"form": form, "titulo": "Agregar institucion", "volver_url": "escuela:dashboard"},
    )
