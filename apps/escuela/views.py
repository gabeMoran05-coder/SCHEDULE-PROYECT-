from datetime import date, time
from urllib.parse import quote_plus

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.horarios.models import BloqueHorario, DiaSemana, FichaAsignacion, HorarioClase

from .forms import AlumnoForm, AsignacionMateriaForm, CicloEscolarForm, DocenteForm, DocumentoAlumnoForm, GrupoForm, InstitucionForm, MateriaForm, MovimientoDocenteForm
from .models import Alumno, AsignacionDocenteMateria, CicloEscolar, ContratoDocente, Docente, DocumentoAlumno, Grupo, Inscripcion, Institucion, KardexAlumno, KardexDocente, Materia
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


def _registrar_kardex_docente(
    request,
    docente,
    tipo,
    referencia="",
    descripcion="",
    contrato=None,
    horas_antes=0,
    horas_despues=0,
    motivo="",
    documento_referencia="",
):
    KardexDocente.objects.create(
        docente=docente,
        contrato=contrato,
        tipo=tipo,
        motivo=motivo,
        referencia=referencia,
        descripcion=descripcion,
        documento_referencia=documento_referencia,
        horas_antes=horas_antes,
        horas_despues=horas_despues,
        horas_movimiento=horas_despues - horas_antes,
        responsable=request.user if request.user.is_authenticated else None,
    )


def _registrar_kardex_alumno(request, alumno, tipo, referencia="", descripcion="", inscripcion=None):
    KardexAlumno.objects.create(
        alumno=alumno,
        inscripcion=inscripcion,
        tipo=tipo,
        referencia=referencia,
        descripcion=descripcion,
        responsable=request.user if request.user.is_authenticated else None,
    )


@login_required
def dashboard(request):
    institucion = get_selected_institution(request)
    ciclo_activo = get_selected_cycle(request)
    ubicacion = ""
    if institucion:
        ubicacion = institucion.direccion.strip()
        if not ubicacion and "ricardo flores magon" in institucion.nombre.lower():
            ubicacion = "Manzanillo, Colima"
    map_query = "Secundaria Ricardo Flores Magon Manzanillo Colima"
    if institucion:
        map_query = f"{institucion.nombre} {ubicacion}".strip()
        if "ricardo flores magon" in institucion.nombre.lower():
            map_query = "19.0237294,-104.3233727"
    context = {
        "total_instituciones": Institucion.objects.count(),
        "institucion_actual": institucion,
        "ciclo_activo": ciclo_activo,
        "ubicacion": ubicacion,
        "map_embed_url": f"https://www.google.com/maps?q={quote_plus(map_query)}&output=embed",
        "total_alumnos": Alumno.objects.filter(institucion=institucion, activo=True).count() if institucion else 0,
        "total_docentes": ContratoDocente.objects.filter(institucion=institucion, ciclo=ciclo_activo, activo=True).count() if institucion and ciclo_activo else 0,
        "total_contratos": ContratoDocente.objects.filter(institucion=institucion, ciclo=ciclo_activo, activo=True).count() if institucion and ciclo_activo else 0,
        "total_grupos": Grupo.objects.filter(ciclo=ciclo_activo).count() if ciclo_activo else 0,
        "total_materias": Materia.objects.filter(institucion=institucion).count() if institucion else 0,
        "total_periodos": ciclo_activo.periodos.count() if ciclo_activo else 0,
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
    ciclo = get_selected_cycle(request)
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activo")
    grado = request.GET.get("grado", "")
    grupo_id = request.GET.get("grupo", "")

    inscripciones_qs = Inscripcion.objects.select_related("alumno", "alumno__institucion", "alumno__tutor", "grupo").filter(
        ciclo=ciclo,
        alumno__institucion=institucion,
    )
    if busqueda:
        inscripciones_qs = inscripciones_qs.filter(
            Q(alumno__matricula__icontains=busqueda)
            | Q(alumno__nombres__icontains=busqueda)
            | Q(alumno__apellidos__icontains=busqueda)
            | Q(alumno__tutor__nombre__icontains=busqueda)
        )
    if grado:
        inscripciones_qs = inscripciones_qs.filter(grupo__grado=grado)
    if grupo_id:
        inscripciones_qs = inscripciones_qs.filter(grupo_id=grupo_id)
    if estado == "oculto":
        inscripciones_qs = inscripciones_qs.filter(alumno__activo=False)
    elif estado != "todos":
        inscripciones_qs = inscripciones_qs.filter(alumno__activo=True)

    grupos = Grupo.objects.filter(ciclo=ciclo, activo=True).order_by("grado", "letra") if ciclo else Grupo.objects.none()
    inscripciones_qs = inscripciones_qs.order_by("grupo__grado", "grupo__letra", "numero_lista", "alumno__apellidos")[:300]

    return render(
        request,
        "escuela/alumnos/index.html",
        {
            "inscripciones": inscripciones_qs,
            "grupos": grupos,
            "busqueda": busqueda,
            "estado": estado,
            "grado": grado,
            "grupo_id": grupo_id,
            "total_alumnos_ciclo": Inscripcion.objects.filter(ciclo=ciclo, alumno__institucion=institucion).count() if ciclo else 0,
        },
    )


@login_required
def alumno_crear(request):
    institucion = get_selected_institution(request)
    form = AlumnoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        alumno = form.save(commit=False)
        alumno.institucion = institucion
        if alumno.tutor and not alumno.tutor.pk:
            alumno.tutor.save()
        alumno.save()
        _registrar_kardex_alumno(
            request,
            alumno,
            KardexAlumno.TipoMovimiento.ALTA,
            referencia=alumno.matricula,
            descripcion="Alta manual de alumno.",
        )
        messages.success(request, "Alumno registrado correctamente.")
        return redirect("escuela:alumnos")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Agregar alumno", "volver_url": "escuela:alumnos"})


@login_required
def alumno_editar(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, institucion=get_selected_institution(request))
    form = AlumnoForm(request.POST or None, instance=alumno)
    if request.method == "POST" and form.is_valid():
        form.save()
        _registrar_kardex_alumno(
            request,
            alumno,
            KardexAlumno.TipoMovimiento.EDICION,
            referencia="Ficha del alumno",
            descripcion="Actualizacion de datos generales, tutor, emergencia o datos medicos.",
        )
        messages.success(request, "Alumno actualizado correctamente.")
        return redirect("escuela:alumno_detalle", alumno_id=alumno.id)
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Editar alumno", "volver_url": "escuela:alumnos"})


@login_required
def alumno_toggle_activo(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, institucion=get_selected_institution(request))
    if request.method == "POST":
        alumno.activo = not alumno.activo
        alumno.save(update_fields=["activo"])
        _registrar_kardex_alumno(
            request,
            alumno,
            KardexAlumno.TipoMovimiento.RESTAURACION if alumno.activo else KardexAlumno.TipoMovimiento.BAJA,
            referencia="Estado del alumno",
            descripcion="Alumno restaurado en el sistema." if alumno.activo else "Alumno ocultado del listado operativo.",
            inscripcion=alumno.inscripcion_set.filter(ciclo=get_selected_cycle(request)).first(),
        )
        messages.success(request, "Alumno restaurado correctamente." if alumno.activo else "Alumno ocultado correctamente.")
    return redirect(request.POST.get("next") or "escuela:alumnos")


@login_required
def alumno_detalle(request, alumno_id):
    alumno = get_object_or_404(Alumno.objects.select_related("institucion", "tutor"), id=alumno_id, institucion=get_selected_institution(request))
    ciclo = get_selected_cycle(request)
    inscripcion = alumno.inscripcion_set.select_related("grupo", "ciclo").filter(ciclo=ciclo).first()
    kardex_alumno = alumno.kardex.select_related("responsable", "inscripcion__grupo")[:20]
    documentos = alumno.documentos.select_related("responsable")[:20]
    documento_form = DocumentoAlumnoForm()
    context = {
        "alumno": alumno,
        "inscripcion": inscripcion,
        "kardex_alumno": kardex_alumno,
        "documentos": documentos,
        "documento_form": documento_form,
    }
    return render(request, "escuela/alumnos/detalle.html", context)


@login_required
def alumno_documento_crear(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, institucion=get_selected_institution(request))
    form = DocumentoAlumnoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        documento = form.save(commit=False)
        documento.alumno = alumno
        documento.responsable = request.user
        documento.save()
        _registrar_kardex_alumno(
            request,
            alumno,
            KardexAlumno.TipoMovimiento.DOCUMENTO,
            referencia=documento.get_tipo_display(),
            descripcion=f"Documento subido: {documento.nombre}",
            inscripcion=alumno.inscripcion_set.filter(ciclo=get_selected_cycle(request)).first(),
        )
        messages.success(request, "Documento cargado correctamente.")
    elif request.method == "POST":
        messages.error(request, "Revisa los datos del documento.")
    return redirect("escuela:alumno_detalle", alumno_id=alumno.id)


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
                horas_antes = asignacion.horas_semanales if asignacion else 0
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

                grupos_texto = ", ".join(f"{grupo.grado}{grupo.letra}" for grupo in form.cleaned_data["grupos"])
                _registrar_kardex_docente(
                    request,
                    docente,
                    KardexDocente.TipoMovimiento.ASIGNACION,
                    referencia=f"{materia.nombre} - {grupos_texto}",
                    descripcion="Asignacion o ajuste de materia en el ciclo seleccionado.",
                    contrato=contrato,
                    horas_antes=horas_antes,
                    horas_despues=asignacion.horas_semanales,
                )
                messages.success(request, "Materia asignada correctamente.")
                return redirect("escuela:docente_detalle", docente_id=docente.id)
        elif action == "quitar_materia":
            asignacion = get_object_or_404(AsignacionDocenteMateria, id=request.POST.get("asignacion_id"), contrato=contrato)
            materia = asignacion.materia
            grupos_texto = ", ".join(f"{grupo.grado}{grupo.letra}" for grupo in asignacion.grupos.all())
            horas_antes = asignacion.horas_semanales
            asignacion.delete()
            _registrar_kardex_docente(
                request,
                docente,
                KardexDocente.TipoMovimiento.RETIRO,
                referencia=f"{materia.nombre} - {grupos_texto}",
                descripcion="Retiro de materia asignada. Estas horas deben revisarse para redistribucion.",
                contrato=contrato,
                horas_antes=horas_antes,
                horas_despues=0,
            )
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
    carga_redistribuir = []
    for asignacion in asignaciones:
        grupos = list(asignacion.grupos.all())
        carga_redistribuir.append(
            {
                "materia": asignacion.materia,
                "grupos": grupos,
                "horas_por_grupo": asignacion.horas_semanales,
                "horas_totales": asignacion.horas_semanales * len(grupos),
            }
        )
    total_redistribuir = sum(item["horas_totales"] for item in carga_redistribuir)
    kardex_docente = docente.kardex.select_related("responsable", "contrato__institucion", "contrato__ciclo")[:12]

    context = {
        "docente": docente,
        "contrato": contrato,
        "asignaciones": asignaciones,
        "form": form,
        "horas_asignadas": horas_asignadas,
        "horas_disponibles": horas_disponibles,
        "dias": DiaSemana.choices,
        "horario_docente": horario_docente,
        "kardex_docente": kardex_docente,
        "carga_redistribuir": carga_redistribuir,
        "total_redistribuir": total_redistribuir,
    }
    return render(request, "escuela/docentes/detalle.html", context)


@login_required
def docente_crear(request):
    form = DocenteForm(request.POST or None, request.FILES or None)
    ciclo_activo = get_selected_cycle(request)

    if request.method == "POST" and form.is_valid():
        docente = form.save()
        if ciclo_activo:
            contrato, _ = ContratoDocente.objects.update_or_create(
                docente=docente,
                institucion=ciclo_activo.institucion,
                ciclo=ciclo_activo,
                defaults={
                    "horas_semanales": form.cleaned_data["horas_semanales"],
                    "es_tutor": form.cleaned_data["es_tutor"],
                    "activo": True,
                },
            )
            _registrar_kardex_docente(
                request,
                docente,
                KardexDocente.TipoMovimiento.ALTA,
                referencia=f"{ciclo_activo.institucion.nombre} - {ciclo_activo.nombre}",
                descripcion="Alta de docente en la escuela y ciclo seleccionados.",
                contrato=contrato,
                horas_antes=0,
                horas_despues=contrato.horas_semanales,
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
    form = DocenteForm(request.POST or None, request.FILES or None, instance=docente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Docente actualizado correctamente.")
        return redirect("escuela:docentes")
    return render(request, "escuela/formulario.html", {"form": form, "titulo": "Editar docente", "volver_url": "escuela:docentes"})


@login_required
def docente_toggle_activo(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id, contratos__institucion=get_selected_institution(request))
    contrato = docente.contratos.filter(institucion=get_selected_institution(request), ciclo=get_selected_cycle(request)).first()
    horas_actuales = contrato.horas_semanales if contrato else 0
    movimiento = "restaurar" if not docente.activo else "ocultar"
    form = MovimientoDocenteForm(request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next") or "escuela:docentes"

    if request.method == "POST":
        if not form.is_valid():
            return render(
                request,
                "escuela/docentes/movimiento.html",
                {"docente": docente, "contrato": contrato, "form": form, "movimiento": movimiento, "next_url": next_url},
            )

        docente.activo = not docente.activo
        docente.save(update_fields=["activo"])
        if docente.activo:
            _registrar_kardex_docente(
                request,
                docente,
                KardexDocente.TipoMovimiento.RESTAURACION,
                referencia="Restauracion de docente",
                descripcion=form.cleaned_data["descripcion"],
                contrato=contrato,
                horas_antes=0,
                horas_despues=horas_actuales,
                motivo=form.cleaned_data["motivo"],
                documento_referencia=form.cleaned_data["documento_referencia"],
            )
        else:
            _registrar_kardex_docente(
                request,
                docente,
                KardexDocente.TipoMovimiento.BAJA,
                referencia="Ocultamiento o baja operativa",
                descripcion=form.cleaned_data["descripcion"],
                contrato=contrato,
                horas_antes=horas_actuales,
                horas_despues=0,
                motivo=form.cleaned_data["motivo"],
                documento_referencia=form.cleaned_data["documento_referencia"],
            )
        messages.success(request, "Docente restaurado correctamente." if docente.activo else "Docente ocultado correctamente.")
        return redirect(next_url)

    return render(
        request,
        "escuela/docentes/movimiento.html",
        {"docente": docente, "contrato": contrato, "form": form, "movimiento": movimiento, "next_url": next_url},
    )


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
