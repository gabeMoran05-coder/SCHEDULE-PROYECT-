import json
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.escuela.models import CicloEscolar, Grupo
from apps.escuela.selectors import get_selected_cycle, get_selected_institution

from .models import BloqueHorario, DiaSemana, FichaAsignacion, HorarioClase, HorarioGrupoGuardado


@login_required
def index(request):
    institucion = get_selected_institution(request)
    horarios = HorarioClase.objects.select_related("grupo", "materia", "contrato__docente", "bloque").filter(ciclo__institucion=institucion)[:80]
    return render(request, "horarios/index.html", {"horarios": horarios})


@login_required
def tablero(request):
    ciclo = get_selected_cycle(request)
    grupos = Grupo.objects.filter(ciclo=ciclo).order_by("grado", "letra") if ciclo else []
    bloques = BloqueHorario.objects.filter(ciclo=ciclo) if ciclo else []
    fichas_qs = FichaAsignacion.objects.select_related(
        "asignacion__contrato__docente",
        "asignacion__materia",
        "grupo",
    ).prefetch_related("clases_colocadas")
    if ciclo:
        fichas_qs = fichas_qs.filter(grupo__ciclo=ciclo)

    colocadas_por_ficha = dict(
        HorarioClase.objects.filter(ciclo=ciclo, ficha__isnull=False)
        .values("ficha_id")
        .annotate(total=Count("id"))
        .values_list("ficha_id", "total")
    ) if ciclo else {}
    fichas = []
    tray_por_docente = {}
    for ficha in fichas_qs[:200]:
        colocadas = colocadas_por_ficha.get(ficha.id, 0)
        ficha.horas_restantes = max(ficha.horas_por_colocar - colocadas, 0)
        fichas.append(ficha)
        docente = ficha.asignacion.contrato.docente
        key = ficha.asignacion.contrato_id
        if key not in tray_por_docente:
            tray_por_docente[key] = {
                "docente": docente,
                "horas_restantes": 0,
                "fichas": [],
            }
        tray_por_docente[key]["horas_restantes"] += ficha.horas_restantes
        tray_por_docente[key]["fichas"].append(ficha)

    clases = (
        HorarioClase.objects.select_related("ficha", "materia", "contrato__docente", "bloque", "grupo")
        .filter(ciclo=ciclo)
        if ciclo
        else []
    )
    clases_por_celda = {(clase.grupo_id, clase.bloque_id, clase.dia): clase for clase in clases}
    boards = []
    for grupo in grupos:
        rows = []
        for bloque in bloques:
            rows.append(
                {
                    "bloque": bloque,
                    "cells": [
                        {
                            "dia_value": dia_value,
                            "dia_label": dia_label,
                            "clase": clases_por_celda.get((grupo.id, bloque.id, dia_value)),
                        }
                        for dia_value, dia_label in DiaSemana.choices
                    ],
                }
            )
        boards.append(
            {
                "grupo": grupo,
                "rows": rows,
                "last_saved": getattr(getattr(grupo, "estado_horario", None), "actualizado_en", None),
            }
        )

    context = {
        "ciclo": ciclo,
        "grupos": grupos,
        "boards": boards,
        "bloques": bloques,
        "dias": DiaSemana.choices,
        "tray_docentes": tray_por_docente.values(),
    }
    return render(request, "horarios/tablero.html", context)


@login_required
def guardar_grupo(request, grupo_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Metodo no permitido."}, status=405)

    ciclo = get_selected_cycle(request)
    grupo = get_object_or_404(Grupo, id=grupo_id, ciclo=ciclo)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Datos invalidos."}, status=400)

    clases = data.get("clases", [])
    if not isinstance(clases, list):
        return JsonResponse({"ok": False, "error": "Formato de clases invalido."}, status=400)

    bloques_validos = set(BloqueHorario.objects.filter(ciclo=ciclo).values_list("id", flat=True))
    dias_validos = {dia for dia, _ in DiaSemana.choices}
    conteo_fichas = defaultdict(int)
    nuevas_clases = []

    for item in clases:
        ficha_id = item.get("ficha_id")
        dia = item.get("dia")
        bloque_id = item.get("bloque_id")

        if not ficha_id or dia not in dias_validos or bloque_id not in bloques_validos:
            return JsonResponse({"ok": False, "error": "Hay una celda con datos incompletos."}, status=400)

        ficha = get_object_or_404(
            FichaAsignacion.objects.select_related("asignacion__materia", "asignacion__contrato", "grupo"),
            id=ficha_id,
        )
        if ficha.grupo_id != grupo.id:
            return JsonResponse(
                {"ok": False, "error": f"La ficha de {ficha.grupo} no pertenece al grupo {grupo}."},
                status=400,
            )
        if ficha.asignacion.materia.grado != grupo.grado:
            return JsonResponse(
                {"ok": False, "error": "La materia no corresponde al grado de este grupo."},
                status=400,
            )

        conteo_fichas[ficha.id] += 1
        if conteo_fichas[ficha.id] > ficha.horas_por_colocar:
            return JsonResponse(
                {"ok": False, "error": f"{ficha.asignacion.materia.nombre} de {grupo} excede sus horas."},
                status=400,
            )

        existe_empalme = HorarioClase.objects.filter(
            ciclo=ciclo,
            contrato=ficha.asignacion.contrato,
            dia=dia,
            bloque_id=bloque_id,
        ).exclude(grupo=grupo).exists()
        if existe_empalme:
            return JsonResponse(
                {"ok": False, "error": f"{ficha.asignacion.contrato.docente} ya tiene clase en ese horario."},
                status=400,
            )

        nuevas_clases.append(
            HorarioClase(
                ciclo=ciclo,
                periodo=ciclo.periodos.order_by("numero").first(),
                grupo=grupo,
                materia=ficha.asignacion.materia,
                contrato=ficha.asignacion.contrato,
                ficha=ficha,
                dia=dia,
                bloque_id=bloque_id,
                aula=ficha.aula or grupo.aula_base,
            )
        )

    with transaction.atomic():
        HorarioClase.objects.filter(ciclo=ciclo, grupo=grupo).delete()
        HorarioClase.objects.bulk_create(nuevas_clases)
        estado, _ = HorarioGrupoGuardado.objects.update_or_create(grupo=grupo, defaults={})

    restantes = {}
    fichas_grupo = FichaAsignacion.objects.filter(grupo=grupo).annotate(colocadas=Count("clases_colocadas"))
    for ficha in fichas_grupo:
        restantes[str(ficha.id)] = max(ficha.horas_por_colocar - ficha.colocadas, 0)

    return JsonResponse(
        {
            "ok": True,
            "last_saved": estado.actualizado_en.strftime("%d/%m/%Y %H:%M"),
            "restantes": restantes,
        }
    )
