from datetime import date, time

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.horarios.models import BloqueHorario, DiaSemana, FichaAsignacion, HorarioClase

from .forms import AlumnoForm, AsignacionMateriaForm, CicloEscolarForm, DocenteForm, GrupoForm, InstitucionForm, MateriaForm
from .models import Alumno, AsignacionDocenteMateria, CicloEscolar, ContratoDocente, Docente, Grupo, Institucion, Materia
from .selectors import get_selected_cycle, get_selected_institution


def _default_cycle_name():
    today = date.today()
    start_year = today.year if today.month >= 8 else today.year - 1
    return f"{start_year}-{start_year + 1}"


def _ensure_school_base(institucion):
    ciclo, _ = CicloEscolar.objects.get_or_create(
        institucion=institucion,
        nombre=_default_cycle_name(),
        defaults={"activo": True},
    )
    CicloEscolar.objects.filter(institucion=institucion).exclude(id=ciclo.id).update(activo=False)

    for numero in range(1, 4):
        ciclo.periodos.get_or_create(numero=numero, defaults={"nombre": f"Periodo {numero}"})

    from apps.horarios.models import BloqueHorario

    bloques = [
        (1, time(7, 0), time(7, 50), False),
        (2, time(7, 50), time(8, 40), False),
        (3, time(8, 40), time(9, 30), False),
        (4, time(9, 30), time(9, 50), True),
        (5, time(9, 50), time(10, 40), False),
        (6, time(10, 40), time(11, 30), False),
        (7, time(11, 30), time(12, 20), False),
        (8, time(12, 20), time(13, 10), False),
    ]
    for orden, inicio, fin, es_receso in bloques:
        BloqueHorario.objects.get_or_create(
            ciclo=ciclo,
            orden=orden,
            defaults={"hora_inicio": inicio, "hora_fin": fin, "es_receso": es_receso},
        )
    return ciclo


def _apply_sort(request, queryset, allowed, default):
    sort = request.GET.get("sort", default)
    direction = request.GET.get("dir", "asc")
    if sort not in allowed:
        sort = default
    order_field = allowed[sort]
    if direction == "desc":
        order_field = f"-{order_field}"
    return queryset.order_by(order_field), sort, direction


def _apply_estado(queryset, estado):
    if estado == "oculto":
        return queryset.filter(activo=False)
    if estado == "todos":
        return queryset
    return queryset.filter(activo=True)


@login_required
def dashboard(request):
    institucion = get_selected_institution(request)
    ciclo_activo = get_selected_cycle(request)
    context = {
        "total_instituciones": Institucion.objects.count(),
        "institucion_actual": institucion,
        "ciclo_activo": ciclo_activo,
        "total_alumnos": Alumno.objects.filter(institucion=institucion, activo=True).count() if institucion else 0,
        "total_docentes": ContratoDocente.objects.filter(institucion=institucion, ciclo=ciclo_activo, activo=True).count() if institucion and ciclo_activo else 0,
        "total_contratos": ContratoDocente.objects.filter(institucion=institucion, ciclo=ciclo_activo, activo=True).count() if institucion and ciclo_activo else 0,
        "total_grupos": Grupo.objects.filter(ciclo=ciclo_activo).count() if ciclo_activo else 0,
        "total_materias": Materia.objects.filter(institucion=institucion).count() if institucion else 0,
    }
    return render(request, "escuela/dashboard.html", context)


@login_required
def seleccionar_institucion(request):
    institucion_id = request.POST.get("institucion_id")
    if institucion_id and Institucion.objects.filter(id=institucion_id).exists():
        request.session["selected_institution_id"] = int(institucion_id)
        request.session.pop("selected_cycle_id", None)
        messages.success(request, "Escuela seleccionada correctamente.")
    return redirect(request.POST.get("next") or "escuela:dashboard")


@login_required
def seleccionar_ciclo(request):
    ciclo_id = request.POST.get("ciclo_id")
    institucion = get_selected_institution(request)
    if ciclo_id and CicloEscolar.objects.filter(id=ciclo_id, institucion=institucion).exists():
        request.session["selected_cycle_id"] = int(ciclo_id)
        messages.success(request, "Ciclo escolar seleccionado correctamente.")
    return redirect(request.POST.get("next") or "escuela:dashboard")


@login_required
def alumnos(request):
    institucion = get_selected_institution(request)
    alumnos_qs = Alumno.objects.select_related("institucion", "tutor").filter(institucion=institucion)
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activo")

    if busqueda:
        alumnos_qs = alumnos_qs.filter(
            Q(matricula__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(tutor__nombre__icontains=busqueda)
        )
    alumnos_qs = _apply_estado(alumnos_qs, estado)
    alumnos_qs, sort, direction = _apply_sort(
        request,
        alumnos_qs,
        {"matricula": "matricula", "nombre": "apellidos", "tutor": "tutor__nombre", "estado": "activo"},
        "nombre",
    )

    alumnos_qs = alumnos_qs[:80]
    return render(
        request,
        "escuela/alumnos/index.html",
        {"alumnos": alumnos_qs, "busqueda": busqueda, "estado": estado, "sort": sort, "dir": direction},
    )


@login_required
def alumno_crear(request):
    institucion = get_selected_institution(request)
    form = AlumnoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        alumno = form.save(commit=False)
        alumno.institucion = institucion
        alumno.save()
        messages.success(request, "Alumno registrado correctamente.")
        return redirect("escuela:alumnos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar alumno", "volver_url": "escuela:alumnos"})


@login_required
def alumno_editar(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, institucion=get_selected_institution(request))
    form = AlumnoForm(request.POST or None, instance=alumno)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Alumno actualizado correctamente.")
        return redirect("escuela:alumnos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Editar alumno", "volver_url": "escuela:alumnos"})


@login_required
def alumno_toggle_activo(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, institucion=get_selected_institution(request))
    if request.method == "POST":
        alumno.activo = not alumno.activo
        alumno.save(update_fields=["activo"])
        messages.success(request, "Alumno restaurado correctamente." if alumno.activo else "Alumno ocultado correctamente.")
    return redirect(request.POST.get("next") or "escuela:alumnos")


@login_required
def docentes(request):
    institucion = get_selected_institution(request)
    ciclo = get_selected_cycle(request)
    docentes_qs = (
        Docente.objects.filter(contratos__institucion=institucion, contratos__ciclo=ciclo)
        .prefetch_related(
            Prefetch(
                "contratos",
                queryset=ContratoDocente.objects.filter(institucion=institucion, ciclo=ciclo).prefetch_related("asignaciones"),
            )
        )
        .distinct()
    )
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activo")

    if busqueda:
        docentes_qs = docentes_qs.filter(
            Q(numero_empleado__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(correo__icontains=busqueda)
        )
    docentes_qs = _apply_estado(docentes_qs, estado)
    docentes_qs, sort, direction = _apply_sort(
        request,
        docentes_qs,
        {"empleado": "numero_empleado", "nombre": "apellidos", "correo": "correo", "estado": "activo"},
        "nombre",
    )

    docentes_qs = docentes_qs[:80]
    return render(
        request,
        "escuela/docentes/index.html",
        {"docentes": docentes_qs, "busqueda": busqueda, "estado": estado, "sort": sort, "dir": direction},
    )


def _contrato_activo_para_docente(request, docente):
    ciclo_activo = get_selected_cycle(request)
    if not ciclo_activo:
        return None
    contrato, _ = ContratoDocente.objects.get_or_create(
        docente=docente,
        institucion=ciclo_activo.institucion,
        ciclo=ciclo_activo,
        defaults={"horas_semanales": 0, "activo": True},
    )
    return contrato


@login_required
def docente_detalle(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    institucion = get_selected_institution(request)
    if not docente.contratos.filter(institucion=institucion).exists():
        messages.error(request, "Ese docente no pertenece a la escuela seleccionada.")
        return redirect("escuela:docentes")
    contrato = _contrato_activo_para_docente(request, docente)

    if not contrato:
        messages.error(request, "Primero crea un ciclo escolar activo para asignar materias.")
        return redirect("escuela:docentes")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "asignar_materia":
            form = AsignacionMateriaForm(request.POST, ciclo=contrato.ciclo)
            if form.is_valid():
                materia = form.cleaned_data["materia"]
                asignacion = AsignacionDocenteMateria.objects.filter(contrato=contrato, materia=materia).first()
                if asignacion is None:
                    asignacion = form.save(commit=False)
                    asignacion.contrato = contrato
                else:
                    asignacion.horas_semanales = form.cleaned_data["horas_semanales"]
                    asignacion.notas = form.cleaned_data["notas"]

                asignacion.save()
                asignacion.grupos.set(form.cleaned_data["grupos"])

                FichaAsignacion.objects.filter(asignacion=asignacion).exclude(
                    grupo__in=form.cleaned_data["grupos"]
                ).delete()
                for grupo in form.cleaned_data["grupos"]:
                    FichaAsignacion.objects.update_or_create(
                        asignacion=asignacion,
                        grupo=grupo,
                        defaults={
                            "horas_por_colocar": asignacion.horas_semanales,
                            "aula": grupo.aula_base,
                        },
                    )

                messages.success(request, "Materia asignada correctamente.")
                return redirect("escuela:docente_detalle", docente_id=docente.id)
        elif action == "quitar_materia":
            asignacion = get_object_or_404(AsignacionDocenteMateria, id=request.POST.get("asignacion_id"), contrato=contrato)
            asignacion.delete()
            messages.success(request, "Materia desasignada correctamente.")
            return redirect("escuela:docente_detalle", docente_id=docente.id)
    else:
        form = AsignacionMateriaForm(ciclo=contrato.ciclo)

    asignaciones = contrato.asignaciones.select_related("materia").prefetch_related("grupos")
    horas_asignadas = sum(asignacion.horas_semanales for asignacion in asignaciones)
    horas_disponibles = contrato.horas_semanales - horas_asignadas
    bloques = BloqueHorario.objects.filter(ciclo=contrato.ciclo)
    clases = HorarioClase.objects.select_related("materia", "grupo", "bloque").filter(contrato=contrato, ciclo=contrato.ciclo)
    clases_por_celda = {(clase.bloque_id, clase.dia): clase for clase in clases}
    horario_docente = [
        {
            "bloque": bloque,
            "cells": [
                {
                    "dia_value": dia_value,
                    "dia_label": dia_label,
                    "clase": clases_por_celda.get((bloque.id, dia_value)),
                }
                for dia_value, dia_label in DiaSemana.choices
            ],
        }
        for bloque in bloques
    ]

    context = {
        "docente": docente,
        "contrato": contrato,
        "asignaciones": asignaciones,
        "form": form,
        "horas_asignadas": horas_asignadas,
        "horas_disponibles": horas_disponibles,
        "dias": DiaSemana.choices,
        "horario_docente": horario_docente,
    }
    return render(request, "escuela/docentes/detalle.html", context)


@login_required
def docente_crear(request):
    form = DocenteForm(request.POST or None)
    ciclo_activo = get_selected_cycle(request)

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
def docente_editar(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id, contratos__institucion=get_selected_institution(request))
    form = DocenteForm(request.POST or None, instance=docente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Docente actualizado correctamente.")
        return redirect("escuela:docentes")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Editar docente", "volver_url": "escuela:docentes"})


@login_required
def docente_toggle_activo(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id, contratos__institucion=get_selected_institution(request))
    if request.method == "POST":
        docente.activo = not docente.activo
        docente.save(update_fields=["activo"])
        messages.success(request, "Docente restaurado correctamente." if docente.activo else "Docente ocultado correctamente.")
    return redirect(request.POST.get("next") or "escuela:docentes")


@login_required
def grupos(request):
    institucion = get_selected_institution(request)
    ciclo = get_selected_cycle(request)
    grupos_qs = Grupo.objects.select_related("ciclo", "ciclo__institucion").filter(ciclo=ciclo, ciclo__institucion=institucion)
    grado = request.GET.get("grado", "")
    turno = request.GET.get("turno", "")
    estado = request.GET.get("estado", "activo")

    if grado:
        grupos_qs = grupos_qs.filter(grado=grado)
    if turno:
        grupos_qs = grupos_qs.filter(turno=turno)
    grupos_qs = _apply_estado(grupos_qs, estado)
    grupos_qs, sort, direction = _apply_sort(
        request,
        grupos_qs,
        {"grupo": "grado", "turno": "turno", "ciclo": "ciclo__nombre", "aula": "aula_base", "estado": "activo"},
        "grupo",
    )

    grupos_qs = grupos_qs[:80]
    return render(
        request,
        "escuela/grupos/index.html",
        {"grupos": grupos_qs, "grado": grado, "turno": turno, "estado": estado, "sort": sort, "dir": direction},
    )


@login_required
def grupo_crear(request):
    institucion = get_selected_institution(request)
    form = GrupoForm(request.POST or None, institucion=institucion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grupo registrado correctamente.")
        return redirect("escuela:grupos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar grupo", "volver_url": "escuela:grupos"})


@login_required
def grupo_editar(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id, ciclo__institucion=get_selected_institution(request))
    form = GrupoForm(request.POST or None, instance=grupo, institucion=get_selected_institution(request))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grupo actualizado correctamente.")
        return redirect("escuela:grupos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Editar grupo", "volver_url": "escuela:grupos"})


@login_required
def grupo_toggle_activo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id, ciclo__institucion=get_selected_institution(request))
    if request.method == "POST":
        grupo.activo = not grupo.activo
        grupo.save(update_fields=["activo"])
        messages.success(request, "Grupo restaurado correctamente." if grupo.activo else "Grupo ocultado correctamente.")
    return redirect(request.POST.get("next") or "escuela:grupos")


@login_required
def materias(request):
    institucion = get_selected_institution(request)
    materias_qs = Materia.objects.filter(institucion=institucion)
    busqueda = request.GET.get("q", "").strip()
    grado = request.GET.get("grado", "")
    estado = request.GET.get("estado", "activo")

    if busqueda:
        materias_qs = materias_qs.filter(Q(clave__icontains=busqueda) | Q(nombre__icontains=busqueda))
    if grado:
        materias_qs = materias_qs.filter(grado=grado)
    materias_qs = _apply_estado(materias_qs, estado)
    materias_qs, sort, direction = _apply_sort(
        request,
        materias_qs,
        {"clave": "clave", "nombre": "nombre", "grado": "grado", "horas": "horas_semanales", "estado": "activo"},
        "grado",
    )

    materias_qs = materias_qs[:80]
    return render(
        request,
        "escuela/materias/index.html",
        {"materias": materias_qs, "busqueda": busqueda, "grado": grado, "estado": estado, "sort": sort, "dir": direction},
    )


@login_required
def materia_crear(request):
    institucion = get_selected_institution(request)
    form = MateriaForm(request.POST or None, institucion=institucion)
    if request.method == "POST" and form.is_valid():
        materia = form.save(commit=False)
        materia.institucion = institucion
        materia.save()
        messages.success(request, "Materia registrada correctamente.")
        return redirect("escuela:materias")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar materia", "volver_url": "escuela:materias"})


@login_required
def materia_editar(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id, institucion=get_selected_institution(request))
    form = MateriaForm(request.POST or None, instance=materia, institucion=get_selected_institution(request))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Materia actualizada correctamente.")
        return redirect("escuela:materias")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Editar materia", "volver_url": "escuela:materias"})


@login_required
def materia_toggle_activo(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id, institucion=get_selected_institution(request))
    if request.method == "POST":
        materia.activo = not materia.activo
        materia.save(update_fields=["activo"])
        messages.success(request, "Materia restaurada correctamente." if materia.activo else "Materia ocultada correctamente.")
    return redirect(request.POST.get("next") or "escuela:materias")


@login_required
def institucion_crear(request):
    form = InstitucionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        institucion = form.save()
        _ensure_school_base(institucion)
        request.session["selected_institution_id"] = institucion.id
        messages.success(request, "Institucion registrada correctamente.")
        return redirect("escuela:dashboard")
    return render(
        request,
        "escuela/formulario.html",
        {"form": form, "titulo": "Agregar institucion", "volver_url": "escuela:dashboard"},
    )


@login_required
def ciclo_crear(request):
    institucion = get_selected_institution(request)
    form = CicloEscolarForm(request.POST or None, institucion=institucion)
    if request.method == "POST" and form.is_valid():
        ciclo = form.save(commit=False)
        ciclo.institucion = institucion
        if ciclo.activo:
            CicloEscolar.objects.filter(institucion=institucion).update(activo=False)
        ciclo.save()
        for numero in range(1, 4):
            ciclo.periodos.get_or_create(numero=numero, defaults={"nombre": f"Periodo {numero}"})
        request.session["selected_cycle_id"] = ciclo.id
        messages.success(request, "Ciclo escolar registrado correctamente.")
        return redirect("escuela:dashboard")
    return render(
        request,
        "escuela/formulario.html",
        {"form": form, "titulo": "Agregar ciclo escolar", "volver_url": "escuela:dashboard"},
    )
